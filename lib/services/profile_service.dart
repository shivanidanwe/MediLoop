import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/user_model.dart';
import '../models/address_model.dart';
import '../models/prescription_model.dart';
import '../core/constants/api_config.dart';
import 'auth_service.dart';

class ProfileService {
  // Singleton pattern
  static final ProfileService _instance = ProfileService._internal();
  factory ProfileService() => _instance;
  ProfileService._internal();

  UserModel _user = UserModel.empty;
  final List<AddressModel> _addresses = [];
  final List<PrescriptionModel> _prescriptions = [];

  final AuthService _authService = AuthService();

  // Set profile data directly from backend user JSON payload
  void setProfileData(Map<String, dynamic> userMap) {
    _user = UserModel.fromJson(userMap);
    _addresses.clear();
    if (userMap['addresses'] != null && userMap['addresses'] is List) {
      for (var item in userMap['addresses']) {
        if (item is Map<String, dynamic>) {
          _addresses.add(AddressModel.fromJson(item));
        }
      }
    }
    _syncUserAddress();
    _notifyListeners();
  }

  // Fetch API profile and real-time records from backend if logged in
  Future<void> fetchProfileFromServer() async {
    final token = await _authService.getToken();
    if (token == null || token.isEmpty) {
      _user = UserModel.empty;
      _addresses.clear();
      _prescriptions.clear();
      _notifyListeners();
      return;
    }
    final user = await _authService.getMe();
    if (user != null && user.name.isNotEmpty) {
      _user = user;
      
      // Fetch user's saved addresses from backend PostgreSQL database
      try {
        final addrRes = await http.get(
          Uri.parse('${ApiConfig.baseUrl}/users/me/addresses'),
          headers: ApiConfig.headers(token),
        );
        if (addrRes.statusCode == 200) {
          final List addrList = jsonDecode(addrRes.body);
          if (addrList.isNotEmpty) {
            _addresses.clear();
            for (var item in addrList) {
              _addresses.add(AddressModel.fromJson(item));
            }
          }
        }
      } catch (_) {}

      // Fetch user's uploaded prescriptions from backend PostgreSQL database
      await fetchPrescriptionsFromBackend();

      _syncUserAddress();
      _notifyListeners();
    } else {
      _user = UserModel.empty;
      _addresses.clear();
      _prescriptions.clear();
      _notifyListeners();
    }
  }

  /// Syncs all prescription history and extracted texts directly from backend PostgreSQL
  Future<void> fetchPrescriptionsFromBackend() async {
    try {
      final token = await _authService.getToken();
      if (token == null || token.isEmpty) return;

      final rxRes = await http.get(
        Uri.parse('${ApiConfig.baseUrl}/prescriptions/customer'),
        headers: ApiConfig.headers(token),
      );
      if (rxRes.statusCode == 200) {
        final List rxList = jsonDecode(rxRes.body);
        _prescriptions.clear();
        for (var rx in rxList) {
          _prescriptions.add(PrescriptionModel.fromJson(rx));
        }
        _notifyListeners();
      }
    } catch (_) {}
  }

  void logout() {
    _user = UserModel.empty;
    _addresses.clear();
    _prescriptions.clear();
    _notifyListeners();
  }

  // Clear data
  void clearData() {
    _user = UserModel.empty;
    _addresses.clear();
    _prescriptions.clear();
    _notifyListeners();
  }

  // Listeners to notify UI when changes occur
  final List<void Function()> _listeners = [];

  void addListener(void Function() listener) {
    _listeners.add(listener);
  }

  void removeListener(void Function() listener) {
    _listeners.remove(listener);
  }

  void _notifyListeners() {
    for (var listener in _listeners) {
      listener();
    }
  }

  // User details
  UserModel getUser() => _user;

  Future<bool> updateUser(UserModel updatedUser) async {
    _user = updatedUser;
    _notifyListeners();

    try {
      final token = await _authService.getToken();
      if (token == null || token.isEmpty) return false;

      final url = Uri.parse('${ApiConfig.baseUrl}/auth/me');
      final currentYear = DateTime.now().year;
      final birthYear = updatedUser.age > 0 ? (currentYear - updatedUser.age) : 1995;
      final dobStr = "$birthYear-01-01";

      final genderVal = updatedUser.gender.toUpperCase().contains('FEMALE')
          ? 'FEMALE'
          : (updatedUser.gender.toUpperCase().contains('OTHER') ? 'OTHER' : 'MALE');

      final payload = {
        'user_info': {
          'full_name': updatedUser.name,
          'email': updatedUser.email,
          'mobile_number': updatedUser.phoneNumber,
          'gender': genderVal,
          'date_of_birth': dobStr,
          if (updatedUser.profilePic != null) 'profile_image': updatedUser.profilePic,
        },
        'medical_info': {
          'allergies': updatedUser.allergies,
          'chronic_conditions': updatedUser.medicalConditions.join(', '),
        },
        'emergency_contact': {
          'contact_name': 'Emergency Contact',
          'relationship': updatedUser.emergencyRelationship,
          'mobile_number': updatedUser.emergencyPhone.isNotEmpty ? updatedUser.emergencyPhone : updatedUser.phoneNumber,
        }
      };

      final response = await http.put(
        url,
        headers: ApiConfig.headers(token),
        body: jsonEncode(payload),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _user = UserModel.fromJson(data);
        _syncUserAddress();
        _notifyListeners();
        return true;
      }
    } catch (e) {
      // Keep optimistic update if offline
    }
    return false;
  }

  // Address Management
  List<AddressModel> getAddresses() => List.unmodifiable(_addresses);

  Future<void> addAddress(AddressModel address) async {
    _addresses.add(address);
    _syncUserAddress();
    _notifyListeners();

    // Persist to backend PostgreSQL database
    try {
      final token = await _authService.getToken();
      if (token != null && token.isNotEmpty) {
        final url = Uri.parse('${ApiConfig.baseUrl}/users/me/addresses');
        final payload = {
          'address_type': address.label.toUpperCase() == 'WORK' ? 'WORK' : 'HOME',
          'house_number': address.address.contains(',') ? address.address.split(',').first.trim() : 'House 1',
          'street': address.address,
          'city': address.city.isNotEmpty ? address.city : 'Bengaluru',
          'state': address.state.isNotEmpty ? address.state : 'Karnataka',
          'pincode': address.pincode.isNotEmpty ? address.pincode : '560103',
          'is_default_delivery': true,
        };
        final res = await http.post(
          url,
          headers: ApiConfig.headers(token),
          body: jsonEncode(payload),
        );
        if (res.statusCode == 201 || res.statusCode == 200) {
          final data = jsonDecode(res.body);
          // Update id from db
          final idx = _addresses.indexOf(address);
          if (idx != -1 && data['id'] != null) {
            _addresses[idx] = address.copyWith(id: data['id'].toString());
          }
        }
      }
    } catch (_) {}
  }

  Future<void> updateAddress(AddressModel updatedAddress) async {
    final index = _addresses.indexWhere((a) => a.id == updatedAddress.id);
    if (index != -1) {
      _addresses[index] = updatedAddress;
    } else {
      _addresses.add(updatedAddress);
    }
    _syncUserAddress();
    _notifyListeners();

    // Persist to backend PostgreSQL database
    try {
      final token = await _authService.getToken();
      if (token != null && token.isNotEmpty) {
        final addrId = int.tryParse(updatedAddress.id) ?? 1;
        final url = Uri.parse('${ApiConfig.baseUrl}/users/me/addresses/$addrId');
        final payload = {
          'house_number': updatedAddress.address.contains(',') ? updatedAddress.address.split(',').first.trim() : 'House 1',
          'street': updatedAddress.address,
          'city': updatedAddress.city.isNotEmpty ? updatedAddress.city : 'Bengaluru',
          'state': updatedAddress.state.isNotEmpty ? updatedAddress.state : 'Karnataka',
          'pincode': updatedAddress.pincode.isNotEmpty ? updatedAddress.pincode : '560103',
          'is_default_delivery': true,
        };
        await http.put(
          url,
          headers: ApiConfig.headers(token),
          body: jsonEncode(payload),
        );
      }
    } catch (_) {}
  }

  Future<void> deleteAddress(String id) async {
    _addresses.removeWhere((a) => a.id == id);
    _syncUserAddress();
    _notifyListeners();

    try {
      final token = await _authService.getToken();
      if (token != null && token.isNotEmpty) {
        final addrId = int.tryParse(id);
        if (addrId != null) {
          final url = Uri.parse('${ApiConfig.baseUrl}/users/me/addresses/$addrId');
          await http.delete(url, headers: ApiConfig.headers(token));
        }
      }
    } catch (_) {}
  }

  void _syncUserAddress() {
    if (_addresses.isNotEmpty) {
      // Set the first address or 'Home' address as default user address
      final homeAddress = _addresses.firstWhere(
        (a) => a.label.toLowerCase() == 'home',
        orElse: () => _addresses.first,
      );
      _user = _user.copyWith(address: homeAddress.fullAddress);
    } else {
      _user = _user.copyWith(address: "No saved addresses");
    }
  }

  // Prescription Management
  List<PrescriptionModel> getPrescriptions() => List.unmodifiable(_prescriptions);

  void addPrescription(PrescriptionModel prescription) {
    _prescriptions.insert(0, prescription);
    _notifyListeners();
  }

  void deletePrescription(String id) {
    _prescriptions.removeWhere((p) => p.id == id);
    _notifyListeners();
  }
}
