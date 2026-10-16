class PharmacyModel {
  final String pharmacyId;
  final String pharmacyName;
  final String pharmacistName;
  final String registrationNumber;
  final String phone;
  final String email;
  final String address;
  final double rating;
  final String deliveryTime;
  final bool isOpen;

  // Extra UI specific properties
  final String distance;
  final String availabilityStatus; // "Available", "Busy", "Offline"
  final String workingHours;
  final List<String> availableServices;

  PharmacyModel({
    required this.pharmacyId,
    required this.pharmacyName,
    required this.pharmacistName,
    required this.registrationNumber,
    required this.phone,
    required this.email,
    required this.address,
    required this.rating,
    required this.deliveryTime,
    required this.isOpen,
    required this.distance,
    required this.availabilityStatus,
    required this.workingHours,
    required this.availableServices,
  });

  factory PharmacyModel.fromJson(Map<String, dynamic> json) {
    return PharmacyModel(
      pharmacyId: json['pharmacyId'] ?? '',
      pharmacyName: json['pharmacyName'] ?? '',
      pharmacistName: json['pharmacistName'] ?? '',
      registrationNumber: json['registrationNumber'] ?? '',
      phone: json['phone'] ?? '',
      email: json['email'] ?? '',
      address: json['address'] ?? '',
      rating: (json['rating'] as num?)?.toDouble() ?? 0.0,
      deliveryTime: json['deliveryTime'] ?? '',
      isOpen: json['isOpen'] ?? false,
      distance: json['distance'] ?? '0.0 km',
      availabilityStatus: json['availabilityStatus'] ?? 'Available',
      workingHours: json['workingHours'] ?? '9:00 AM - 10:00 PM',
      availableServices: List<String>.from(json['availableServices'] ?? []),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'pharmacyId': pharmacyId,
      'pharmacyName': pharmacyName,
      'pharmacistName': pharmacistName,
      'registrationNumber': registrationNumber,
      'phone': phone,
      'email': email,
      'address': address,
      'rating': rating,
      'deliveryTime': deliveryTime,
      'isOpen': isOpen,
      'distance': distance,
      'availabilityStatus': availabilityStatus,
      'workingHours': workingHours,
      'availableServices': availableServices,
    };
  }
}
