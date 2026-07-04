import '../models/medicine_model.dart';

class MedicineService {
  static List<Category> getCategories() {
    return [
      Category(name: 'Tablets', iconPath: 'tablet'),
      Category(name: 'Syrups', iconPath: 'medication'),
      Category(name: 'Capsules', iconPath: 'medication_liquid'),
      Category(name: 'Vitamins', iconPath: 'health_and_safety'),
      Category(name: 'Baby Care', iconPath: 'child_care'),
      Category(name: 'Skin Care', iconPath: 'face'),
      Category(name: 'First Aid', iconPath: 'medical_information'),
      Category(name: 'Diabetes', iconPath: 'bloodtype'),
    ];
  }

  static List<Medicine> getPopularMedicines() {
    return [
      Medicine(
        id: '1',
        name: 'Crocin 650',
        description: 'Pain Relief & Fever',
        price: 35.0,
        rating: 4.5,
        imageUrl: 'crocin',
      ),
      Medicine(
        id: '2',
        name: 'Vicks Vaporub',
        description: 'Cough & Cold',
        price: 95.0,
        rating: 4.8,
        imageUrl: 'vicks',
      ),
      Medicine(
        id: '3',
        name: 'Dolo 650',
        description: 'Fever Relief',
        price: 30.0,
        rating: 4.7,
        imageUrl: 'dolo',
      ),
    ];
  }

  static List<Offer> getOffers() {
    return [
      Offer(title: '20% OFF', description: 'On first order', code: 'MED20', imagePath: 'offer1'),
      Offer(title: 'Free Delivery', description: 'On orders above ₹500', code: 'FREESHIP', imagePath: 'offer2'),
    ];
  }

  static List<RecentOrder> getRecentOrders() {
    return [
      RecentOrder(id: '101', medicineName: 'Crocin 650', date: '15 June', status: 'Delivered'),
      RecentOrder(id: '102', medicineName: 'Vitamins B12', date: '10 June', status: 'Delivered'),
    ];
  }
}
