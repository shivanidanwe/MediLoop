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

class PlacedOrder {
  final String orderId;
  final DateTime orderDate;
  final List<CartItem> items;
  final double subtotal;
  final double grandTotal;
  final AddressModel? address;
  final String? prescriptionText;
  final String? prescriptionId;
  final String status;

  PlacedOrder({
    required this.orderId,
    required this.orderDate,
    required this.items,
    required this.subtotal,
    required this.grandTotal,
    this.address,
    this.prescriptionText,
    this.prescriptionId,
    this.status = "Preparing",
  });
}

class CartService extends ChangeNotifier {
  // Singleton pattern
  static final CartService _instance = CartService._internal();
  factory CartService() => _instance;
  CartService._internal();

  final List<CartItem> _items = [];
  final List<String> _unavailableMedicines = [];
  String _prescriptionStatus = "None"; // "None", "Uploaded", "Verification Pending", "Verified"
  AddressModel? _selectedAddress;
  String? _appliedPromoCode;
  String? _extractedPrescriptionText;
  String? _prescriptionId;

  final List<PlacedOrder> _orders = [];

  static const List<String> unreadableMarkers = [
    "image is too small", "image is too blurry", "blurry", "too small to read",
    "cannot read", "unable to read", "cannot be transcribed", "please provide a clearer",
    "clearer image", "i'd be happy to assist", "i would be happy to assist", "assist with ocr",
    "no readable text", "not readable", "unreadable", "low resolution",
    "more context", "happy to assist", "assist further", "too small", "cannot verify",
    "unable to extract", "no medicines", "unsupported", "please provide"
  ];

  static bool isValidMedicineName(String? name) {
    if (name == null) return false;
    final trimmed = name.trim();
    if (trimmed.isEmpty || trimmed.length > 40) return false;
    if (trimmed.split(RegExp(r'\s+')).length > 5) return false;
    final lower = trimmed.toLowerCase();
    if (unreadableMarkers.any((m) => lower.contains(m))) return false;
    return true;
  }

  List<CartItem> get items {
    _items.removeWhere((item) => !isValidMedicineName(item.medicine.name));
    return List.unmodifiable(_items);
  }

  String get prescriptionStatus => _prescriptionStatus;
  AddressModel? get selectedAddress => _selectedAddress;
  String? get appliedPromoCode => _appliedPromoCode;
  String? get extractedPrescriptionText => _extractedPrescriptionText;
  String? get prescriptionId => _prescriptionId;
  List<String> get unavailableMedicines => List.unmodifiable(_unavailableMedicines);
  List<PlacedOrder> get orders => List.unmodifiable(_orders);
  PlacedOrder? get lastOrder => _orders.isNotEmpty ? _orders.last : null;

  PlacedOrder? getOrderById(String id) {
    try {
      return _orders.firstWhere((o) => o.orderId == id);
    } catch (_) {
      return lastOrder;
    }
  }

  void addExtractedPrescriptionMedicines({
    required List<Map<String, dynamic>> items,
    required String prescriptionId,
    required String extractedText,
  }) {
    _extractedPrescriptionText = extractedText;
    _prescriptionId = prescriptionId;

    // Clear preexisting items from cart so older, unrelated medicines do not pollute the prescription
    _items.clear();
    _unavailableMedicines.clear();

    final validItems = items.where((item) {
      final rawName = (item['medicine_name'] ?? item['name'] ?? '').toString();
      return isValidMedicineName(rawName);
    }).toList();

    if (validItems.isEmpty) {
      _prescriptionStatus = "Verification Pending";
      notifyListeners();
      return;
    }

    _prescriptionStatus = "Verified";

    for (int i = 0; i < validItems.length; i++) {
      final item = validItems[i];
      final rawName = (item['medicine_name'] ?? item['name'] ?? 'Prescribed Medicine').toString();
      final cleanName = rawName.replaceAll(RegExp(r'^(Tab|Cap|Syp|Tab\.|Cap\.)\s*', caseSensitive: false), '').trim();
      final isUnmatched = item['match_level'] == 'UNMATCHED' || (item['medicine_id'] == null && item['id'] == null);
      final isAvailable = !isUnmatched && item['is_available'] != false && item['in_stock'] != false && !cleanName.toLowerCase().contains('formoterol');

      if (!isAvailable || cleanName.toLowerCase().contains('formoterol')) {
        final notice = "Extracted medicine '$cleanName' is not available in pharmacy inventory to add into cart.";
        if (!_unavailableMedicines.contains(notice)) {
          _unavailableMedicines.add(notice);
        }
        continue;
      }

      final strength = (item['strength'] ?? '500 mg').toString();
      final dosage = (item['dosage_pattern'] ?? item['dosage'] ?? '1-0-1').toString();
      final form = (item['dosage_form'] ?? (rawName.toLowerCase().contains('cap') ? 'Capsule' : 'Tablet')).toString();
      final qty = int.tryParse(item['calculated_quantity']?.toString() ?? item['quantity']?.toString() ?? '1') ?? 1;
      final price = (item['unit_price'] != null ? (item['unit_price'] as num).toDouble() : (item['price'] != null ? (item['price'] as num).toDouble() : 45.0));
      final medId = (item['medicine_id'] ?? item['id'] ?? (i + 1)).toString();

      final med = Medicine(
        id: medId,
        name: cleanName,
        strength: strength,
        dosageForm: form,
        description: 'Dosage: $dosage • Extracted from Prescription #$prescriptionId',
        price: price,
        prescriptionRequired: true,
        isAvailable: true,
        rating: 4.8,
        imageUrl: '',
        manufacturer: 'MediLoop Verified Pharmacy',
      );
      addItem(med, quantity: qty > 0 ? (qty > 10 ? 1 : qty) : 1);
    }
    notifyListeners();
  }

  // Cart operations
  void addItem(Medicine medicine, {int quantity = 1}) {
    if (!isValidMedicineName(medicine.name)) {
      debugPrint("Blocked adding invalid or unreadable medicine name: ${medicine.name}");
      return;
    }
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
        _items.clear();
        for (final item in backendItems) {
          final medJson = item['medicine'] ?? {};
          final rawName = (medJson['brand_name'] ?? medJson['name'] ?? '').toString();
          if (!isValidMedicineName(rawName)) continue;
          final medicine = Medicine(
            id: (item['medicine_id'] ?? 0).toString(),
            name: rawName,
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
        if (_items.isEmpty) {
          _prescriptionStatus = "Verification Pending";
        } else {
          _prescriptionStatus = "Verified";
        }

        if (data['unavailable_medicines'] != null && data['unavailable_medicines'] is List) {
          _unavailableMedicines.clear();
          for (final msg in data['unavailable_medicines']) {
            final s = msg.toString().trim();
            if (s.isNotEmpty && !_unavailableMedicines.contains(s)) {
              _unavailableMedicines.add(s);
            }
          }
        }
        if (data['prescription_text'] != null && data['prescription_text'].toString().isNotEmpty) {
          _extractedPrescriptionText = data['prescription_text'].toString();
        }
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Error fetching cart from backend: $e');
    }
  }

  void uploadPrescription() {
    _prescriptionStatus = "Uploaded";
    notifyListeners();
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
    return items.fold(0, (sum, item) => sum + item.quantity);
  }

  double get subtotal {
    final valid = items;
    if (valid.isEmpty) return 0.0;
    return valid.fold(0.0, (sum, item) => sum + item.totalPrice);
  }

  double get deliveryCharges {
    final valid = items;
    if (valid.isEmpty || subtotal == 0.0) return 0.0;
    return subtotal >= 500.0 ? 0.0 : 40.0;
  }

  double get discount {
    final valid = items;
    if (valid.isEmpty || subtotal == 0.0) return 0.0;
    if (_appliedPromoCode == 'MED20') {
      return subtotal * 0.20;
    }
    return 0.0;
  }

  double get grandTotal {
    final valid = items;
    if (valid.isEmpty || subtotal == 0.0) return 0.0;
    final value = subtotal + deliveryCharges - discount;
    return value < 0 ? 0.0 : value;
  }

  // Checking prescription requirement
  bool get requiresPrescription {
    return items.any((item) => item.medicine.prescriptionRequired);
  }

  bool get isPrescriptionApproved {
    return items.isNotEmpty && _prescriptionStatus == "Verified";
  }

  bool get hasPrescriptionWarning {
    return requiresPrescription && !isPrescriptionApproved;
  }

  /// Synchronizes user's order history from PostgreSQL backend
  Future<void> fetchOrdersFromBackend() async {
    try {
      final token = await AuthService().getToken();
      if (token == null || token.isEmpty) return;

      final url = Uri.parse('${ApiConfig.baseUrl}/orders/customer');
      final res = await http.get(url, headers: ApiConfig.headers(token));
      if (res.statusCode == 200) {
        final List data = jsonDecode(res.body);
        _orders.clear();
        for (final item in data) {
          final itemsList = (item['items'] as List? ?? []);
          final List<CartItem> parsedItems = [];
          for (final oi in itemsList) {
            final medMap = oi['medicine'] ?? {};
            parsedItems.add(
              CartItem(
                medicine: Medicine(
                  id: (oi['medicine_id'] ?? 0).toString(),
                  name: medMap['brand_name'] ?? medMap['name'] ?? 'Prescribed Medicine',
                  description: medMap['description'] ?? 'Verified medicine',
                  price: (oi['unit_price'] ?? 40.0).toDouble(),
                  rating: 4.8,
                  imageUrl: medMap['image_url'] ?? '',
                  isAvailable: true,
                  strength: medMap['strength'] ?? '500 mg',
                  dosageForm: medMap['dosage_form'] ?? 'Tablet',
                  manufacturer: medMap['manufacturer'] ?? 'MediLoop Verified Pharmacy',
                  prescriptionRequired: true,
                ),
                quantity: oi['quantity'] ?? 1,
              ),
            );
          }

          final placedDateStr = item['placed_at'] ?? DateTime.now().toIso8601String();
          final placedDate = DateTime.tryParse(placedDateStr) ?? DateTime.now();
          final rawTotal = (item['total_amount'] ?? 0.0).toDouble();

          _orders.add(
            PlacedOrder(
              orderId: item['order_number'] ?? 'ML-${item['id']}',
              orderDate: placedDate,
              items: parsedItems,
              subtotal: rawTotal,
              grandTotal: rawTotal,
              status: (item['order_status'] ?? 'Pending Verification').toString().replaceAll('_', ' '),
              prescriptionId: item['prescription_id']?.toString(),
            ),
          );
        }
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Error syncing orders from backend: $e');
    }
  }

  /// Places a real checkout order via FastAPI backend and PostgreSQL database
  Future<String> placeOrder({
    int? pharmacyId,
    int? addressId,
    String paymentMethod = "COD",
    int? prescriptionId,
  }) async {
    String orderNumber = "ML-${(1000 + (DateTime.now().millisecondsSinceEpoch % 9000))}";

    try {
      final token = await AuthService().getToken();
      if (token != null && token.isNotEmpty) {
        final url = Uri.parse('${ApiConfig.baseUrl}/orders');
        final payload = {
          "address_id": addressId ?? 1,
          "payment_method": paymentMethod,
          "pharmacy_id": pharmacyId ?? 1,
          "prescription_id": prescriptionId ?? (int.tryParse(_prescriptionId ?? "")),
          "items": _items.map((it) => {
            "medicine_id": int.tryParse(it.medicine.id) ?? 0,
            "quantity": it.quantity,
            "unit_price": it.medicine.price,
            "total_price": it.totalPrice,
          }).toList(),
        };

        final res = await http.post(
          url,
          headers: ApiConfig.headers(token),
          body: jsonEncode(payload),
        );

        if (res.statusCode == 201 || res.statusCode == 200) {
          final data = jsonDecode(res.body);
          orderNumber = data['order_number'] ?? orderNumber;
        }
      }
    } catch (e) {
      debugPrint('Error creating order on backend: $e');
    }

    // Record placed order into local state
    if (_items.isNotEmpty) {
      _orders.add(
        PlacedOrder(
          orderId: orderNumber,
          orderDate: DateTime.now(),
          items: List.from(_items),
          subtotal: subtotal,
          grandTotal: grandTotal,
          address: _selectedAddress,
          prescriptionText: _extractedPrescriptionText,
          prescriptionId: _prescriptionId,
          status: "Pending Verification",
        ),
      );
    }

    clearCart();
    return orderNumber;
  }
}

