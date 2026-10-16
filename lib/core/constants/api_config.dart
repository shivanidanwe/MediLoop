import 'package:flutter/foundation.dart';

class ApiConfig {
  // Base URL for local development
  // 10.0.2.2 is the Android emulator's loopback alias to localhost
  static String get baseUrl {
    if (kIsWeb) {
      return 'http://localhost:8000/api/v1';
    } else if (defaultTargetPlatform == TargetPlatform.android) {
      return 'http://10.0.2.2:8000/api/v1';
    } else {
      return 'http://localhost:8000/api/v1';
    }
  }

  // Auth endpoints
  static String get loginUrl => '$baseUrl/auth/login';
  static String get registerUrl => '$baseUrl/auth/register';
  static String get meUrl => '$baseUrl/auth/me';
  static String get forgotPasswordUrl => '$baseUrl/auth/forgot-password';
  static String get verifyOtpUrl => '$baseUrl/auth/verify-otp';
  static String get resetPasswordUrl => '$baseUrl/auth/reset-password';

  // Request headers helper
  static Map<String, String> headers([String? token]) {
    final map = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (token != null && token.isNotEmpty) {
      map['Authorization'] = 'Bearer $token';
    }
    return map;
  }
}
