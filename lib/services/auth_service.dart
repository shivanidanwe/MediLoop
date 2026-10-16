import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../core/constants/api_config.dart';
import '../models/user_model.dart';
import 'profile_service.dart';

class AuthService {
  static const String _tokenKey = 'auth_token';
  static const String _userKey = 'user_profile';

  final http.Client _client;

  AuthService({http.Client? client}) : _client = client ?? http.Client();

  /// Retrieve stored JWT Access Token
  Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  /// Check if user is currently logged in
  Future<bool> isLoggedIn() async {
    final token = await getToken();
    return token != null && token.isNotEmpty;
  }

  /// Authenticate user credentials with FastAPI backend
  Future<Map<String, dynamic>> login(String email, String password) async {
    final url = Uri.parse(ApiConfig.loginUrl);
    try {
      final response = await _client.post(
        url,
        headers: ApiConfig.headers(),
        body: jsonEncode({
          'email': email.trim(),
          'password': password,
        }),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        final token = data['access_token'] as String;
        final userMap = data['user'] as Map<String, dynamic>;

        // Store JWT token & cached user profile
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString(_tokenKey, token);
        await prefs.setString(_userKey, jsonEncode(userMap));

        // Sync ProfileService state
        ProfileService().setProfileData(userMap);

        return {
          'success': true,
          'token': token,
          'user': UserModel.fromJson(userMap),
        };
      } else {
        return {
          'success': false,
          'message': data['detail'] ?? 'Login failed. Please check credentials.',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: Unable to connect to server ($e)',
      };
    }
  }

  /// Register a new user profile with FastAPI backend
  Future<Map<String, dynamic>> register({
    required String name,
    required String email,
    required String password,
    required String phoneNumber,
    required int age,
    required String gender,
    required String address,
    required String city,
    required String state,
    required String pincode,
    required List<String> medicalConditions,
    required String allergies,
    required String emergencyRelationship,
    required String emergencyPhone,
  }) async {
    final url = Uri.parse(ApiConfig.registerUrl);

    // Compute approximate Date of Birth from age
    final now = DateTime.now();
    final dob = DateTime(now.year - age, 1, 1).toIso8601String().split('T').first;

    // Convert gender string to enum string format ('Male' -> 'MALE')
    final genderEnum = gender.toUpperCase();

    final payload = {
      'user_info': {
        'full_name': name,
        'email': email.trim(),
        'password': password,
        'mobile_number': phoneNumber,
        'date_of_birth': dob,
        'gender': genderEnum.contains('FEMALE') ? 'FEMALE' : (genderEnum.contains('MALE') ? 'MALE' : 'OTHER'),
        'profile_image': null,
      },
      'home_address': {
        'house_number': '1',
        'street': address,
        'city': city,
        'state': state,
        'pincode': pincode,
        'address_type': 'HOME',
        'is_default_delivery': true,
        'landmark': null,
      },
      'work_address': null,
      'medical_info': {
        'medical_conditions': medicalConditions.isNotEmpty ? medicalConditions.join(', ') : null,
        'allergies': allergies.trim().isNotEmpty ? allergies : null,
      },
      'emergency_contact': {
        'relationship': emergencyRelationship,
        'contact_number': emergencyPhone,
      },
    };

    try {
      final response = await _client.post(
        url,
        headers: ApiConfig.headers(),
        body: jsonEncode(payload),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 201 || response.statusCode == 200) {
        return {
          'success': true,
          'user': UserModel.fromJson(data),
        };
      } else {
        return {
          'success': false,
          'message': data['detail'] ?? 'Registration failed',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: Unable to connect to server ($e)',
      };
    }
  }

  /// Fetch currently authenticated user's profile (/auth/me)
  Future<UserModel?> getMe() async {
    final token = await getToken();
    if (token == null) return null;

    final url = Uri.parse(ApiConfig.meUrl);
    try {
      final response = await _client.get(
        url,
        headers: ApiConfig.headers(token),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final user = UserModel.fromJson(data);

        // Update cached profile
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString(_userKey, jsonEncode(data));

        return user;
      }
    } catch (_) {}

    // Fallback to cached profile if offline
    return getCachedUser();
  }

  /// Retrieve cached user profile from SharedPreferences
  Future<UserModel?> getCachedUser() async {
    final prefs = await SharedPreferences.getInstance();
    final userJson = prefs.getString(_userKey);
    if (userJson != null) {
      try {
        return UserModel.fromJson(jsonDecode(userJson));
      } catch (_) {}
    }
    return null;
  }

  /// Request real-time OTP for password reset
  Future<Map<String, dynamic>> forgotPassword(String email) async {
    final url = Uri.parse(ApiConfig.forgotPasswordUrl);
    try {
      final response = await _client.post(
        url,
        headers: ApiConfig.headers(),
        body: jsonEncode({'email': email.trim()}),
      );
      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        return {'success': true, 'message': data['message']};
      } else {
        return {'success': false, 'message': data['detail'] ?? 'Failed to send OTP'};
      }
    } catch (e) {
      return {'success': false, 'message': 'Network error: $e'};
    }
  }

  /// Verify OTP code with backend
  Future<Map<String, dynamic>> verifyOtp(String email, String otp) async {
    final url = Uri.parse(ApiConfig.verifyOtpUrl);
    try {
      final response = await _client.post(
        url,
        headers: ApiConfig.headers(),
        body: jsonEncode({'email': email.trim(), 'otp': otp.trim()}),
      );
      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        return {'success': true, 'message': data['message']};
      } else {
        return {'success': false, 'message': data['detail'] ?? 'Invalid OTP code'};
      }
    } catch (e) {
      return {'success': false, 'message': 'Network error: $e'};
    }
  }

  /// Reset password using verified OTP code
  Future<Map<String, dynamic>> resetPassword(String email, String otp, String newPassword) async {
    final url = Uri.parse(ApiConfig.resetPasswordUrl);
    try {
      final response = await _client.post(
        url,
        headers: ApiConfig.headers(),
        body: jsonEncode({'email': email.trim(), 'otp': otp.trim(), 'new_password': newPassword}),
      );
      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        return {'success': true, 'message': data['message']};
      } else {
        return {'success': false, 'message': data['detail'] ?? 'Failed to reset password'};
      }
    } catch (e) {
      return {'success': false, 'message': 'Network error: $e'};
    }
  }

  /// Logout current user and clear tokens
  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_userKey);
    ProfileService().logout();
  }
}
