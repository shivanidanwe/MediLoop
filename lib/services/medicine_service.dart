import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/constants/api_config.dart';
import '../models/medicine_model.dart';
import 'auth_service.dart';

class MedicineService {
  static final List<Category> _defaultCategories = [
    Category(name: 'Tablets', iconPath: 'tablet'),
    Category(name: 'Syrups', iconPath: 'medication'),
    Category(name: 'Capsules', iconPath: 'medication_liquid'),
    Category(name: 'Vitamins', iconPath: 'health_and_safety'),
    Category(name: 'Baby Care', iconPath: 'child_care'),
    Category(name: 'Skin Care', iconPath: 'face'),
    Category(name: 'First Aid', iconPath: 'medical_information'),
    Category(name: 'Diabetes', iconPath: 'bloodtype'),
  ];

  static final List<Offer> _defaultOffers = [
    Offer(title: '20% OFF', description: 'On first order', code: 'MED20', imagePath: 'offer1'),
    Offer(title: 'Free Delivery', description: 'On orders above ₹500', code: 'FREESHIP', imagePath: 'offer2'),
  ];

  /// Fetches product categories
  static Future<List<Category>> fetchCategories() async {
    return _defaultCategories;
  }

  /// Fetches offers and coupons
  static Future<List<Offer>> fetchOffers() async {
    return _defaultOffers;
  }

  /// Fetches popular medicines directly from backend PostgreSQL database
  static Future<List<Medicine>> fetchPopularMedicines() async {
    try {
      final url = Uri.parse('${ApiConfig.baseUrl}/medicines?limit=8');
      final res = await http.get(url, headers: ApiConfig.headers());
      if (res.statusCode == 200) {
        final List data = jsonDecode(res.body);
        return data.map((json) => Medicine.fromJson(json)).toList();
      }
    } catch (_) {}
    return [];
  }

  /// Fallback catalog medicines to guarantee the catalog is never blank
  static final List<Medicine> _fallbackMedicines = [
    Medicine(
      id: "1",
      name: "Crocin 650",
      description: "Effective fast relief from high fever, mild to moderate headache and body pain.",
      price: 35.0,
      rating: 4.9,
      imageUrl: "",
      strength: "650 mg",
      dosageForm: "Tablet",
      manufacturer: "GlaxoSmithKline Pharmaceuticals",
      prescriptionRequired: false,
    ),
    Medicine(
      id: "3",
      name: "Dolo 650",
      description: "Paracetamol 650mg tablets for fever reduction and anti-inflammatory relief.",
      price: 30.0,
      rating: 4.8,
      imageUrl: "",
      strength: "650 mg",
      dosageForm: "Tablet",
      manufacturer: "Micro Labs Ltd",
      prescriptionRequired: false,
    ),
    Medicine(
      id: "4",
      name: "Calpol 500",
      description: "Analgesic and antipyretic tablets for gentle, reliable fever relief.",
      price: 24.0,
      rating: 4.7,
      imageUrl: "",
      strength: "500 mg",
      dosageForm: "Tablet",
      manufacturer: "GlaxoSmithKline",
      prescriptionRequired: false,
    ),
    Medicine(
      id: "2",
      name: "Amoxil 500",
      description: "Broad-spectrum bactericidal antibiotic capsule used to treat respiratory & bacterial infections.",
      price: 120.0,
      rating: 4.8,
      imageUrl: "",
      strength: "500 mg",
      dosageForm: "Capsule",
      manufacturer: "GlaxoSmithKline",
      prescriptionRequired: true,
    ),
    Medicine(
      id: "12",
      name: "Cifran 500",
      description: "Ciprofloxacin broad spectrum fluoroquinolone antibiotic.",
      price: 95.0,
      rating: 4.6,
      imageUrl: "",
      strength: "500 mg",
      dosageForm: "Tablet",
      manufacturer: "Sun Pharma Ltd",
      prescriptionRequired: true,
    ),
    Medicine(
      id: "15",
      name: "Lipitor 10",
      description: "Atorvastatin lipid-lowering medication for cardiovascular wellness and cholesterol management.",
      price: 165.0,
      rating: 4.9,
      imageUrl: "",
      strength: "10 mg",
      dosageForm: "Tablet",
      manufacturer: "Pfizer India Ltd",
      prescriptionRequired: true,
    ),
    Medicine(
      id: "20",
      name: "Benadryl Cough Syrup",
      description: "Soothing anti-tussive and mucolytic syrup for acute dry and allergic coughs.",
      price: 110.0,
      rating: 4.7,
      imageUrl: "",
      strength: "100 ml",
      dosageForm: "Syrup",
      manufacturer: "Johnson & Johnson",
      prescriptionRequired: false,
    ),
    Medicine(
      id: "22",
      name: "Glucophage 500",
      description: "Metformin hydrochloride tablets for glycemic control and type 2 diabetes management.",
      price: 85.0,
      rating: 4.8,
      imageUrl: "",
      strength: "500 mg",
      dosageForm: "Tablet",
      manufacturer: "Merck India",
      prescriptionRequired: true,
    ),
    Medicine(
      id: "25",
      name: "Ascoril-D Plus Syrup",
      description: "Dextromethorphan + Chlorpheniramine + Phenylephrine cough relief formulation.",
      price: 125.0,
      rating: 4.6,
      imageUrl: "",
      strength: "100 ml",
      dosageForm: "Syrup",
      manufacturer: "Glenmark Pharmaceuticals",
      prescriptionRequired: false,
    ),
    Medicine(
      id: "32",
      name: "Budecort 200 Inhaler",
      description: "Budesonide pressurized inhalation suspension for management of chronic asthma and bronchospasm.",
      price: 280.0,
      rating: 4.9,
      imageUrl: "",
      strength: "200 mcg",
      dosageForm: "Inhaler",
      manufacturer: "Cipla Ltd",
      prescriptionRequired: true,
    ),
    Medicine(
      id: "41",
      name: "Shelcal 500",
      description: "Calcium carbonate and Vitamin D3 dietary supplement for strong bone density.",
      price: 115.0,
      rating: 4.8,
      imageUrl: "",
      strength: "500 mg",
      dosageForm: "Tablet",
      manufacturer: "Torrent Pharma",
      prescriptionRequired: false,
    ),
    Medicine(
      id: "48",
      name: "Becosules Z Capsules",
      description: "B-Complex forte with Vitamin C and Zinc capsules for physical endurance & immunity.",
      price: 52.0,
      rating: 4.9,
      imageUrl: "",
      strength: "Z-Formula",
      dosageForm: "Capsule",
      manufacturer: "Pfizer India Ltd",
      prescriptionRequired: false,
    ),
  ];

  /// Fetches all active catalog medicines from backend PostgreSQL database
  static Future<List<Medicine>> fetchMedicines({int limit = 60}) async {
    try {
      final url = Uri.parse('${ApiConfig.baseUrl}/medicines?limit=$limit');
      final res = await http.get(url, headers: ApiConfig.headers());
      if (res.statusCode == 200) {
        final List data = jsonDecode(res.body);
        if (data.isNotEmpty) {
          return data.map((json) => Medicine.fromJson(json)).toList();
        }
      }
    } catch (_) {}
    return _fallbackMedicines;
  }

  /// Searches medicines via PostgreSQL full-text/fuzzy search API
  static Future<List<Medicine>> searchMedicines(String query) async {
    final cleanQuery = query.trim();
    if (cleanQuery.isEmpty) return [];

    try {
      final url = Uri.parse('${ApiConfig.baseUrl}/medicines/search?q=${Uri.encodeComponent(cleanQuery)}');
      final res = await http.get(url, headers: ApiConfig.headers());
      if (res.statusCode == 200) {
        final List data = jsonDecode(res.body);
        return data.map((json) => Medicine.fromJson(json)).toList();
      }
    } catch (_) {}
    return [];
  }

  /// Retrieves a specific medicine by ID from PostgreSQL database
  static Future<Medicine?> getMedicineDetails(String id) async {
    try {
      final url = Uri.parse('${ApiConfig.baseUrl}/medicines/$id');
      final res = await http.get(url, headers: ApiConfig.headers());
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        return Medicine.fromJson(data);
      }
    } catch (_) {}
    return null;
  }

  /// Fetches real customer orders directly from backend PostgreSQL database
  static Future<List<RecentOrder>> fetchRecentOrders() async {
    try {
      final token = await AuthService().getToken();
      if (token == null || token.isEmpty) return [];

      final url = Uri.parse('${ApiConfig.baseUrl}/orders/customer');
      final res = await http.get(url, headers: ApiConfig.headers(token));
      if (res.statusCode == 200) {
        final List data = jsonDecode(res.body);
        final List<RecentOrder> recent = [];
        for (final item in data) {
          final itemsList = item['items'] as List? ?? [];
          String medSummary = 'Prescribed Medicines';
          if (itemsList.isNotEmpty) {
            final firstMed = itemsList.first['medicine'];
            if (firstMed != null) {
              medSummary = firstMed['brand_name'] ?? firstMed['name'] ?? medSummary;
              if (itemsList.length > 1) {
                medSummary += ' + ${itemsList.length - 1} more';
              }
            }
          }
          final placedAt = item['placed_at']?.toString().split('T').first ?? 'Recent';
          recent.add(
            RecentOrder(
              id: item['order_number'] ?? 'ML-${item['id']}',
              medicineName: medSummary,
              date: placedAt,
              status: (item['order_status'] ?? 'Delivered').toString().replaceAll('_', ' '),
            ),
          );
        }
        return recent;
      }
    } catch (_) {}
    return [];
  }
}
