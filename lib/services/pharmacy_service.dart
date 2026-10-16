import '../models/pharmacy_model.dart';

class PharmacyService {
  // Singleton pattern
  static final PharmacyService _instance = PharmacyService._internal();
  factory PharmacyService() => _instance;
  PharmacyService._internal();

  final List<PharmacyModel> _mockPharmacies = [
    PharmacyModel(
      pharmacyId: "ph-1",
      pharmacyName: "MediCare Pharmacy",
      pharmacistName: "Dr. Rahul Sharma",
      registrationNumber: "MH-PH-123456",
      phone: "+91 9876543210",
      email: "pharmacy@email.com",
      address: "Baner Road, Pune",
      rating: 4.8,
      deliveryTime: "25 Minutes",
      isOpen: true,
      distance: "1.2 km",
      availabilityStatus: "Available",
      workingHours: "9:00 AM - 10:00 PM",
      availableServices: [
        "Prescription Verification",
        "Home Delivery",
        "Emergency Medicines",
        "AI Assisted Ordering"
      ],
    ),
    PharmacyModel(
      pharmacyId: "ph-2",
      pharmacyName: "Wellness Pharmacy",
      pharmacistName: "Dr. Priya Patel",
      registrationNumber: "MH-PH-654321",
      phone: "+91 9823456789",
      email: "priya.wellness@email.com",
      address: "Kalyani Nagar, Pune",
      rating: 4.5,
      deliveryTime: "15 Minutes",
      isOpen: true,
      distance: "0.8 km",
      availabilityStatus: "Available",
      workingHours: "8:00 AM - 11:00 PM",
      availableServices: [
        "Prescription Verification",
        "Home Delivery",
        "AI Assisted Ordering"
      ],
    ),
    PharmacyModel(
      pharmacyId: "ph-3",
      pharmacyName: "Apollo Pharmacy",
      pharmacistName: "Dr. Amit Verma",
      registrationNumber: "MH-PH-789012",
      phone: "+91 9812345670",
      email: "amit.apollo@email.com",
      address: "Viman Nagar, Pune",
      rating: 4.6,
      deliveryTime: "30 Minutes",
      isOpen: false,
      distance: "3.5 km",
      availabilityStatus: "Offline",
      workingHours: "9:00 AM - 9:00 PM",
      availableServices: [
        "Prescription Verification",
        "Home Delivery",
        "Emergency Medicines"
      ],
    ),
    PharmacyModel(
      pharmacyId: "ph-4",
      pharmacyName: "City Medicos",
      pharmacistName: "Dr. K. S. Rao",
      registrationNumber: "MH-PH-345678",
      phone: "+91 9901234567",
      email: "city.medicos@email.com",
      address: "Kothrud, Pune",
      rating: 4.2,
      deliveryTime: "45 Minutes",
      isOpen: true,
      distance: "5.0 km",
      availabilityStatus: "Busy",
      workingHours: "10:00 AM - 10:00 PM",
      availableServices: [
        "Prescription Verification",
        "Emergency Medicines"
      ],
    ),
  ];

  /// Simulates a network request to search for pharmacies based on delivery location pincode.
  /// If the pincode is '411001' or '411006' (Pune), it returns list.
  /// For any other pincodes, it returns empty list to demonstrate empty state.
  Future<List<PharmacyModel>> getPharmaciesForAddress(String? pincode) async {
    // Simulate network delay to trigger loading skeletons
    await Future.delayed(const Duration(milliseconds: 1500));

    if (pincode == null || pincode.trim().isEmpty) {
      return [];
    }

    // Supported pincodes in Pune
    if (pincode == "411001" || pincode == "411006") {
      return List.unmodifiable(_mockPharmacies);
    }

    // Returns empty list for any other pincodes
    return [];
  }
}
