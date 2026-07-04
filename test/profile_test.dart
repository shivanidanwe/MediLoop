import 'package:flutter_test/flutter_test.dart';
import 'package:mediloop/models/user_model.dart';
import 'package:mediloop/models/address_model.dart';
import 'package:mediloop/models/prescription_model.dart';
import 'package:mediloop/services/profile_service.dart';

void main() {
  group('MediLoop Profile Models & Service Tests', () {
    late ProfileService profileService;

    setUp(() {
      profileService = ProfileService();
    });

    test('UserModel mock values are loaded correctly', () {
      final user = profileService.getUser();
      expect(user.name, equals('Shivani Danwe'));
      expect(user.email, equals('shivani@gmail.com'));
      expect(user.gender, equals('Female'));
      expect(user.age, equals(26));
      expect(user.medicalConditions, contains('Diabetes'));
      expect(user.medicalConditions, contains('Hypertension'));
      expect(user.allergies, contains('Penicillin'));
      expect(user.emergencyRelationship, equals('Brother'));
      expect(user.emergencyPhone, equals('+91 9988776655'));
    });

    test('UserModel copyWith works correctly', () {
      final user = profileService.getUser();
      final updated = user.copyWith(
        name: 'New Name',
        age: 30,
        gender: 'Male',
      );
      expect(updated.name, equals('New Name'));
      expect(updated.age, equals(30));
      expect(updated.gender, equals('Male'));
      // Unchanged fields remain same
      expect(updated.email, equals(user.email));
    });

    test('AddressModel properties and helper getters work correctly', () {
      final address = AddressModel(
        id: '99',
        label: 'Home',
        address: '123 Main St',
        city: 'Mumbai',
        state: 'Maharashtra',
        pincode: '400001',
      );
      expect(address.fullAddress, equals('123 Main St, Mumbai, Maharashtra - 400001'));
    });

    test('ProfileService updates user and notifies listeners', () {
      final user = profileService.getUser();
      bool listenerNotified = false;

      void listener() {
        listenerNotified = true;
      }

      profileService.addListener(listener);

      final updatedUser = user.copyWith(name: 'Updated Listener Name');
      profileService.updateUser(updatedUser);

      expect(profileService.getUser().name, equals('Updated Listener Name'));
      expect(listenerNotified, isTrue);

      profileService.removeListener(listener);
    });

    test('ProfileService manages addresses and synchronizes user default address', () {
      final initialCount = profileService.getAddresses().length;
      final newAddress = AddressModel(
        id: 'addr_temp',
        label: 'Office',
        address: '456 Business Rd',
        city: 'Pune',
        state: 'Maharashtra',
        pincode: '411011',
      );

      profileService.addAddress(newAddress);
      expect(profileService.getAddresses().length, equals(initialCount + 1));

      // Update address
      final updatedAddress = newAddress.copyWith(address: '789 Business Rd Updated');
      profileService.updateAddress(updatedAddress);
      expect(profileService.getAddresses().firstWhere((a) => a.id == 'addr_temp').address, equals('789 Business Rd Updated'));

      // Delete address
      profileService.deleteAddress('addr_temp');
      expect(profileService.getAddresses().length, equals(initialCount));
    });

    test('ProfileService manages prescriptions', () {
      final initialCount = profileService.getPrescriptions().length;
      final newPrescription = PrescriptionModel(
        id: 'rx_temp',
        uploadDate: '2026-07-03',
        status: 'Pending',
        fileName: 'test_prescription.jpg',
      );

      profileService.addPrescription(newPrescription);
      expect(profileService.getPrescriptions().length, equals(initialCount + 1));
      expect(profileService.getPrescriptions().first.id, equals('rx_temp')); // inserted at index 0

      profileService.deletePrescription('rx_temp');
      expect(profileService.getPrescriptions().length, equals(initialCount));
    });
  });
}
