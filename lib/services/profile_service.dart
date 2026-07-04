import '../models/user_model.dart';
import '../models/address_model.dart';
import '../models/prescription_model.dart';

class ProfileService {
  // Singleton pattern
  static final ProfileService _instance = ProfileService._internal();
  factory ProfileService() => _instance;
  ProfileService._internal();

  UserModel _user = UserModel.mock;
  final List<AddressModel> _addresses = AddressModel.mockAddresses;
  final List<PrescriptionModel> _prescriptions = PrescriptionModel.mockPrescriptions;

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
