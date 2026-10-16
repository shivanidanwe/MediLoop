import '../models/user_model.dart';
import '../models/address_model.dart';
import '../models/prescription_model.dart';
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

  // Fetch API profile from backend if logged in
  Future<void> fetchProfileFromServer() async {
    final token = await _authService.getToken();
    if (token == null || token.isEmpty) {
      resetToMockData();
      return;
    }
    final user = await _authService.getMe();
    if (user != null && user.name.isNotEmpty) {
      _user = user;
      _notifyListeners();
    } else {
      resetToMockData();
    }
  }

  void logout() {
    _user = UserModel.empty;
    _addresses.clear();
    _prescriptions.clear();
    _notifyListeners();
  }

  // Reset/populate with mock data synchronously for testing/debugging
  void resetToMockData() {
    _user = UserModel.mock;
    _addresses.clear();
    _addresses.addAll(AddressModel.mockAddresses);
    _prescriptions.clear();
    _prescriptions.addAll(PrescriptionModel.mockPrescriptions);
    _notifyListeners();
  }

  // Listeners to notify UI when changes occur (simple callback system)
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

  void updateUser(UserModel updatedUser) {
    _user = updatedUser;
    _notifyListeners();
  }

  // Address Management
  List<AddressModel> getAddresses() => List.unmodifiable(_addresses);

  void addAddress(AddressModel address) {
    _addresses.add(address);
    // Sync first address as user address if needed
    _syncUserAddress();
    _notifyListeners();
  }

  void updateAddress(AddressModel updatedAddress) {
    final index = _addresses.indexWhere((a) => a.id == updatedAddress.id);
    if (index != -1) {
      _addresses[index] = updatedAddress;
      _syncUserAddress();
      _notifyListeners();
    }
  }

  void deleteAddress(String id) {
    _addresses.removeWhere((a) => a.id == id);
    _syncUserAddress();
    _notifyListeners();
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
    _prescriptions.insert(0, prescription); // Insert at beginning (newest first)
    _notifyListeners();
  }

  void deletePrescription(String id) {
    _prescriptions.removeWhere((p) => p.id == id);
    _notifyListeners();
  }
}
