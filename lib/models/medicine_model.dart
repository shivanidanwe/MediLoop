class Medicine {
  final String id;
  final String name;
  final String description;
  final double price;
  final double rating;
  final String imageUrl;
  final bool isAvailable;
  final String strength; // e.g. "650 mg", "10 ml"
  final String dosageForm; // e.g. "Tablet", "Syrup", "Capsule"
  final String manufacturer; // e.g. "Cipla Ltd", "GlaxoSmithKline"
  final bool prescriptionRequired;

  Medicine({
    required this.id,
    required this.name,
    required this.description,
    required this.price,
    required this.rating,
    required this.imageUrl,
    this.isAvailable = true,
    required this.strength,
    required this.dosageForm,
    required this.manufacturer,
    required this.prescriptionRequired,
  });

  factory Medicine.fromJson(Map<String, dynamic> json) {
    final rawName = json['brand_name'] ?? json['name'] ?? 'Medicine';
    final priceNum = json['price'] ?? 45.0;
    return Medicine(
      id: (json['id'] ?? 0).toString(),
      name: rawName.toString(),
      description: json['description']?.toString() ?? 'High quality verified pharmaceutical medicine.',
      price: (priceNum as num).toDouble(),
      rating: (json['rating'] != null ? (json['rating'] as num).toDouble() : 4.8),
      imageUrl: json['image_url']?.toString() ?? '',
      isAvailable: json['is_active'] ?? json['is_available'] ?? true,
      strength: json['strength']?.toString() ?? '500 mg',
      dosageForm: json['dosage_form']?.toString() ?? 'Tablet',
      manufacturer: json['manufacturer']?.toString() ?? 'MediLoop Verified Pharmacy',
      prescriptionRequired: json['prescription_required'] ?? false,
    );
  }
}

class Category {
  final String name;
  final String iconPath;

  Category({required this.name, required this.iconPath});
}

class Offer {
  final String title;
  final String description;
  final String code;
  final String imagePath;

  Offer({
    required this.title,
    required this.description,
    required this.code,
    required this.imagePath,
  });
}

class RecentOrder {
  final String id;
  final String medicineName;
  final String date;
  final String status;

  RecentOrder({
    required this.id,
    required this.medicineName,
    required this.date,
    required this.status,
  });
}
