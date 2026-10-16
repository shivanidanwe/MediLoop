import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../core/constants/api_config.dart';
import '../models/medicine_model.dart';
import '../models/address_model.dart';
import 'auth_service.dart';

class CartItem {
  final Medicine medicine;
  int quantity;

  CartItem({required this.medicine, this.quantity = 1});

  double get totalPrice => medicine.price * quantity;
}

class CartService extends ChangeNotifier {
  // Singleton pattern
  static final CartService _instance = CartService._internal();
  factory CartService() => _instance;
  CartService._internal();

  final List<CartItem> _items = [];
  String _prescriptionStatus = "None"; // "None", "Uploaded", "Verification Pending", "Verified"
  AddressModel? _selectedAddress;
  String? _appliedPromoCode;

  List<CartItem> get items => List.unmodifiable(_items);
  String get prescriptionStatus => _prescriptionStatus;
  AddressModel? get selectedAddress => _selectedAddress;
  String? get appliedPromoCode => _appliedPromoCode;

  // Cart operations
  void addItem(Medicine medicine, {int quantity = 1}) {
    final index = _items.indexWhere((item) => item.medicine.id == medicine.id);
    if (index != -1) {
      _items[index].quantity += quantity;
    } else {
      _items.add(CartItem(medicine: medicine, quantity: quantity));
    }
    notifyListeners();
  }

  void removeItem(String id) {
    _items.removeWhere((item) => item.medicine.id == id);
    notifyListeners();
  }

  void updateQuantity(String id, int change) {
    final index = _items.indexWhere((item) => item.medicine.id == id);
    if (index != -1) {
      final newQty = _items[index].quantity + change;
      if (newQty <= 0) {
        _items.removeAt(index);
      } else {
        _items[index].quantity = newQty;
      }
      notifyListeners();
    }
  }

  void clearCart() {
    _items.clear();
    _appliedPromoCode = null;
    notifyListeners();
  }

  // Prescription status operations
  void setPrescriptionStatus(String status) {
    _prescriptionStatus = status;
    notifyListeners();
  }

  /// Syncs active Cart records from PostgreSQL backend into Flutter state
  Future<void> fetchCartFromBackend() async {
    try {
      final token = await AuthService().getToken();
      if (token == null || token.isEmpty) return;

      final url = Uri.parse('${ApiConfig.baseUrl}/cart');
      final res = await http.get(url, headers: ApiConfig.headers(token));
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        final List<dynamic> backendItems = data['items'] ?? [];
        if (backendItems.isNotEmpty) {
          _items.clear();
          for (final item in backendItems) {
            final medJson = item['medicine'] ?? {};
            final medicine = Medicine(
              id: (item['medicine_id'] ?? 0).toString(),
              name: medJson['brand_name'] ?? medJson['name'] ?? 'Prescribed Medicine',
              description: medJson['description'] ?? 'Added from verified prescription',
              price: (item['unit_price'] ?? 40.0).toDouble(),
              rating: 4.8,
              imageUrl: medJson['image_url'] ?? '',
              isAvailable: true,
              strength: medJson['strength'] ?? '500 mg',
              dosageForm: medJson['dosage_form'] ?? 'Tablet',
              manufacturer: medJson['manufacturer'] ?? 'MediLoop Verified Pharmacy',
              prescriptionRequired: true,
            );
            _items.add(CartItem(
              medicine: medicine,
              quantity: item['quantity'] ?? 1,
            ));
          }
          _prescriptionStatus = "Verified";
          notifyListeners();
        }
      }
    } catch (e) {
      debugPrint('Error fetching cart from backend: $e');
    }
  }

  void uploadPrescription() {
    _prescriptionStatus = "Uploaded";
    notifyListeners();
    
    // Simulate prescription verification flow after 5 seconds
    Future.delayed(const Duration(seconds: 4), () {
      _prescriptionStatus = "Verification Pending";
      notifyListeners();
    });

    Future.delayed(const Duration(seconds: 8), () {
      _prescriptionStatus = "Verified";
      notifyListeners();
    });
  }

  void removePrescription() {
    _prescriptionStatus = "None";
    notifyListeners();
  }

  // Address selection
  void selectAddress(AddressModel address) {
    _selectedAddress = address;
    notifyListeners();
  }

  // Promo code
  void applyPromoCode(String code) {
    _appliedPromoCode = code;
    notifyListeners();
  }

  void removePromoCode() {
    _appliedPromoCode = null;
    notifyListeners();
  }

  // Calculations
  int get totalMedicinesCount {
    return _items.fold(0, (sum, item) => sum + item.quantity);
  }

  double get subtotal {
    return _items.fold(0.0, (sum, item) => sum + item.totalPrice);
  }

  double get deliveryCharges {
    if (subtotal == 0) return 0.0;
    return subtotal >= 500.0 ? 0.0 : 40.0;
  }

  double get discount {
    if (_appliedPromoCode == 'MED20') {
      return subtotal * 0.20;
    }
    return 0.0;
  }

  double get grandTotal {
    final value = subtotal + deliveryCharges - discount;
    return value < 0 ? 0.0 : value;
  }

  // Checking prescription requirement
  bool get requiresPrescription {
    return _items.any((item) => item.medicine.prescriptionRequired);
  }

  bool get isPrescriptionApproved {
    return _prescriptionStatus == "Verified";
  }

  bool get hasPrescriptionWarning {
    return requiresPrescription && _prescriptionStatus != "Verified";
  }

  // Check out simulation
  Future<String> placeOrder() async {
    await Future.delayed(const Duration(milliseconds: 1500));
    final orderId = "ML-${(1000 + (DateTime.now().millisecondsSinceEpoch % 9000))}";
    clearCart();
    return orderId;
  }
}
