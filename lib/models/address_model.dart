class AddressModel {
  final String id;
  final String label; // "Home", "Office", "Other"
  final String address;
  final String city;
  final String state;
  final String pincode;

  AddressModel({
    required this.id,
    required this.label,
    required this.address,
    required this.city,
    required this.state,
    required this.pincode,
  });

  AddressModel copyWith({
    String? id,
    String? label,
    String? address,
    String? city,
    String? state,
    String? pincode,
  }) {
    return AddressModel(
      id: id ?? this.id,
      label: label ?? this.label,
      address: address ?? this.address,
      city: city ?? this.city,
      state: state ?? this.state,
      pincode: pincode ?? this.pincode,
    );
  }

  String get fullAddress => "$address, $city, $state - $pincode";

  factory AddressModel.fromJson(Map<String, dynamic> json) {
    String street = json['street'] ?? json['address'] ?? '';
    if (json['house_number'] != null && json['house_number'].toString().isNotEmpty) {
      street = "${json['house_number']}, $street";
    }
    return AddressModel(
      id: json['id']?.toString() ?? DateTime.now().millisecondsSinceEpoch.toString(),
      label: json['address_type'] ?? json['label'] ?? 'Home',
      address: street,
      city: json['city'] ?? '',
      state: json['state'] ?? '',
      pincode: json['pincode'] ?? '',
    );
  }

  static List<AddressModel> get mockAddresses => [
        AddressModel(
          id: "1",
          label: "Home",
          address: "Flat 203, Rosewood Apartments",
          city: "Pune",
          state: "Maharashtra",
          pincode: "411001",
        ),
        AddressModel(
          id: "2",
          label: "Office",
          address: "10th Floor, Tech Park, Kalyani Nagar",
          city: "Pune",
          state: "Maharashtra",
          pincode: "411006",
        ),
      ];
}
