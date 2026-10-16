import '../models/medicine_model.dart';

class MedicineService {
  // A simulated remote database of medicines
  static final List<Medicine> _remoteDatabase = [
    Medicine(
      id: '1',
      name: 'Crocin 650',
      description: 'Provides relief from pain and fever by blocking chemical messengers in the brain.',
      price: 35.0,
      rating: 4.5,
      imageUrl: 'tablet',
      strength: '650 mg',
      dosageForm: 'Tablet',
      manufacturer: 'GlaxoSmithKline plc',
      prescriptionRequired: false,
    ),
    Medicine(
      id: '2',
      name: 'Vicks Vaporub',
      description: 'Ointment for cold and cough relief. Applied on chest, neck, and back.',
      price: 95.0,
      rating: 4.8,
      imageUrl: 'medication_liquid',
      strength: '50 g',
      dosageForm: 'Ointment',
      manufacturer: 'Procter & Gamble',
      prescriptionRequired: false,
    ),
    Medicine(
      id: '3',
      name: 'Dolo 650',
      description: 'Used for fever and mild-to-moderate pain relief. Highly recommended antipyretic.',
      price: 30.0,
      rating: 4.7,
      imageUrl: 'tablet',
      strength: '650 mg',
      dosageForm: 'Tablet',
      manufacturer: 'Micro Labs Ltd',
      prescriptionRequired: false,
    ),
    Medicine(
      id: '4',
      name: 'Amoxicillin 500',
      description: 'Broad-spectrum penicillin antibiotic used to treat bacterial infections.',
      price: 120.0,
      rating: 4.6,
      imageUrl: 'capsule',
      strength: '500 mg',
      dosageForm: 'Capsule',
      manufacturer: 'Alkem Laboratories',
      prescriptionRequired: true,
    ),
    Medicine(
      id: '5',
      name: 'Combiflam',
      description: 'Combination of Ibuprofen and Paracetamol. Reduces inflammation and relieves severe pain.',
      price: 45.0,
      rating: 4.4,
      imageUrl: 'tablet',
      strength: '400 mg + 325 mg',
      dosageForm: 'Tablet',
      manufacturer: 'Sanofi India Ltd',
      prescriptionRequired: false,
    ),
    Medicine(
      id: '6',
      name: 'Benadryl Cough Syrup',
      description: 'Soothes throat irritation and relieves dry cough and cold symptoms.',
      price: 105.0,
      rating: 4.3,
      imageUrl: 'medication',
      strength: '100 ml',
      dosageForm: 'Syrup',
      manufacturer: 'Johnson & Johnson',
      prescriptionRequired: false,
    ),
    Medicine(
      id: '7',
      name: 'Atorvastatin 10',
      description: 'Statins used to lower cholesterol and reduce the risk of heart disease.',
      price: 85.0,
      rating: 4.9,
      imageUrl: 'tablet',
      strength: '10 mg',
      dosageForm: 'Tablet',
      manufacturer: 'Zydus Cadila',
      prescriptionRequired: true,
    ),
    Medicine(
      id: '8',
      name: 'Metformin 500',
      description: 'Oral diabetes medicine that helps control blood sugar levels for Type-2 Diabetes.',
      price: 55.0,
      rating: 4.8,
      imageUrl: 'tablet',
      strength: '500 mg',
      dosageForm: 'Tablet',
      manufacturer: 'Abbott Healthcare',
      prescriptionRequired: true,
    ),
  ];

  static final List<Category> _remoteCategories = [
    Category(name: 'Tablets', iconPath: 'tablet'),
    Category(name: 'Syrups', iconPath: 'medication'),
    Category(name: 'Capsules', iconPath: 'medication_liquid'),
    Category(name: 'Vitamins', iconPath: 'health_and_safety'),
    Category(name: 'Baby Care', iconPath: 'child_care'),
    Category(name: 'Skin Care', iconPath: 'face'),
    Category(name: 'First Aid', iconPath: 'medical_information'),
    Category(name: 'Diabetes', iconPath: 'bloodtype'),
  ];

  static final List<Offer> _remoteOffers = [
    Offer(title: '20% OFF', description: 'On first order', code: 'MED20', imagePath: 'offer1'),
    Offer(title: 'Free Delivery', description: 'On orders above ₹500', code: 'FREESHIP', imagePath: 'offer2'),
  ];

  // Asynchronous API calls representing backend fetching with latency
  static Future<List<Category>> fetchCategories() async {
    await Future.delayed(const Duration(milliseconds: 800));
    return _remoteCategories;
  }

  static Future<List<Medicine>> fetchPopularMedicines() async {
    await Future.delayed(const Duration(milliseconds: 1000));
    // Return a subset of database as popular items
    return _remoteDatabase.sublist(0, 3);
  }

  static Future<List<Offer>> fetchOffers() async {
    await Future.delayed(const Duration(milliseconds: 700));
    return _remoteOffers;
  }

  static Future<List<RecentOrder>> fetchRecentOrders() async {
    await Future.delayed(const Duration(milliseconds: 900));
    return [
      RecentOrder(id: 'ML-9281', medicineName: 'Amoxicillin 500', date: '15 June', status: 'Delivered'),
      RecentOrder(id: 'ML-8491', medicineName: 'Combiflam', date: '10 June', status: 'Delivered'),
    ];
  }

  // Search API
  static Future<List<Medicine>> searchMedicines(String query) async {
    await Future.delayed(const Duration(milliseconds: 800));
    if (query.trim().isEmpty) return [];
    
    final lowercaseQuery = query.toLowerCase();
    return _remoteDatabase.where((med) {
      return med.name.toLowerCase().contains(lowercaseQuery) ||
             med.description.toLowerCase().contains(lowercaseQuery) ||
             med.manufacturer.toLowerCase().contains(lowercaseQuery) ||
             med.dosageForm.toLowerCase().contains(lowercaseQuery);
    }).toList();
  }

  // Get single medicine detail from API
  static Future<Medicine?> getMedicineDetails(String id) async {
    await Future.delayed(const Duration(milliseconds: 500));
    try {
      return _remoteDatabase.firstWhere((med) => med.id == id);
    } catch (_) {
      return null;
    }
  }
}
