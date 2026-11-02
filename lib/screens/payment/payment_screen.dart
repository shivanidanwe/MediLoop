import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../services/cart_service.dart';
import '../../routes/app_routes.dart';
import '../../models/pharmacy_model.dart';
import '../../models/address_model.dart';
import '../../services/pharmacy_service.dart';
import '../../services/profile_service.dart';

class PaymentScreen extends StatefulWidget {
  const PaymentScreen({super.key});

  @override
  State<PaymentScreen> createState() => _PaymentScreenState();
}

class _PaymentScreenState extends State<PaymentScreen> {
  final CartService _cartService = CartService();
  final PharmacyService _pharmacyService = PharmacyService();
  final ProfileService _profileService = ProfileService();

  final _formKey = GlobalKey<FormState>();
  final TextEditingController _searchController = TextEditingController();
  final TextEditingController _instructionsController = TextEditingController();
  final TextEditingController _altContactController = TextEditingController();
  final TextEditingController _notesController = TextEditingController();

  List<PharmacyModel> _pharmacies = [];
  List<PharmacyModel> _filteredPharmacies = [];
  PharmacyModel? _selectedPharmacy;

  bool _isLoadingPharmacies = true;
  bool _isPlacingOrder = false;
  String _searchQuery = "";
  String _selectedSlot = "Earliest Available";

  final List<String> _slots = [
    "Earliest Available",
    "Morning (8:00 AM - 12:00 PM)",
    "Afternoon (12:00 PM - 4:00 PM)",
    "Evening (4:00 PM - 8:00 PM)"
  ];

  @override
  void initState() {
    super.initState();
    _loadPharmacies();
  }

  @override
  void dispose() {
    _searchController.dispose();
    _instructionsController.dispose();
    _altContactController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _loadPharmacies() async {
    setState(() {
      _isLoadingPharmacies = true;
    });

    final address = _cartService.selectedAddress;
    final pincode = address?.pincode;

    final list = await _pharmacyService.getPharmaciesForAddress(pincode);

    if (mounted) {
      setState(() {
        _pharmacies = list;
        _filteredPharmacies = list;
        _isLoadingPharmacies = false;

        // Auto-select the first open pharmacy
        final openPharmacies = list.where((p) => p.isOpen).toList();
        if (openPharmacies.isNotEmpty) {
          _selectedPharmacy = openPharmacies.first;
        } else if (list.isNotEmpty) {
          _selectedPharmacy = list.first;
        } else {
          _selectedPharmacy = null;
        }
      });
    }
  }

  void _onSearchChanged(String query) {
    setState(() {
      _searchQuery = query;
      _filteredPharmacies = _pharmacies.where((p) {
        final matchesName = p.pharmacyName.toLowerCase().contains(query.toLowerCase());
        final matchesPharmacist = p.pharmacistName.toLowerCase().contains(query.toLowerCase());
        final matchesAddress = p.address.toLowerCase().contains(query.toLowerCase());
        return matchesName || matchesPharmacist || matchesAddress;
      }).toList();
    });
  }

  String? _validateAltContact(String? value) {
    if (value != null && value.trim().isNotEmpty) {
      final digits = value.replaceAll(RegExp(r'\D'), '');
      if (digits.length != 10) {
        return "Please enter a valid 10-digit mobile number";
      }
    }
    return null;
  }

  void _handlePlaceOrder() async {
    if (_formKey.currentState == null || !_formKey.currentState!.validate()) {
      return;
    }

    if (_selectedPharmacy == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Row(
            children: [
              Icon(Icons.error_outline_rounded, color: Colors.white),
              SizedBox(width: 8),
              Text("Please select a pharmacy to fulfill your order."),
            ],
          ),
          backgroundColor: Colors.red.shade800,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        ),
      );
      return;
    }

    setState(() {
      _isPlacingOrder = true;
    });

    final addressId = _cartService.selectedAddress?.id != null 
        ? int.tryParse(_cartService.selectedAddress!.id) ?? 1 
        : 1;
    final pharmacyId = int.tryParse(_selectedPharmacy?.pharmacyId ?? "1") ?? 1;
    final rxId = int.tryParse(_cartService.prescriptionId ?? "");

    final orderId = await _cartService.placeOrder(
      pharmacyId: pharmacyId,
      addressId: addressId,
      paymentMethod: "COD",
      prescriptionId: rxId,
    );

    if (mounted) {
      setState(() {
        _isPlacingOrder = false;
      });
      _showSuccessDialog(orderId);
    }
  }

  void _showSuccessDialog(String orderId) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return PopScope(
          canPop: false, // Prevent dismissing via back button
          child: Dialog(
            backgroundColor: Colors.white,
            surfaceTintColor: Colors.transparent,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(24),
            ),
            elevation: 10,
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 28.0),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // Success Icon Circle
                  Container(
                    width: 78,
                    height: 78,
                    decoration: BoxDecoration(
                      color: AppTheme.secondaryColor.withOpacity(0.5),
                      shape: BoxShape.circle,
                    ),
                    child: Center(
                      child: Container(
                        width: 58,
                        height: 58,
                        decoration: const BoxDecoration(
                          color: AppTheme.primaryColor,
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(
                          Icons.check_rounded,
                          size: 34,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Title
                  const Text(
                    "Order Placed Successfully",
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 18.5,
                      color: AppTheme.textColorPrimary,
                      letterSpacing: -0.3,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 12),

                  // Message
                  Text(
                    "Your selected pharmacy has received the order and the pharmacist will begin verification shortly.",
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: AppTheme.textColorSecondary.withOpacity(0.9),
                      fontSize: 13,
                      height: 1.45,
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Order Details Box
                  Container(
                    padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 16),
                    decoration: BoxDecoration(
                      color: AppTheme.backgroundColor,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: Colors.grey.shade200),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          "Order ID",
                          style: TextStyle(color: AppTheme.textColorSecondary, fontSize: 12.5, fontWeight: FontWeight.w500),
                        ),
                        Text(
                          orderId,
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 14.5,
                            color: AppTheme.primaryColor,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 28),

                  // Navigation Button
                  AnimatedButtonWrapper(
                    onPressed: () {
                      Navigator.pop(context); // Close dialog
                      Navigator.pushNamedAndRemoveUntil(
                        context,
                        AppRoutes.orderSuccess,
                        (route) => route.settings.name == AppRoutes.home,
                        arguments: orderId,
                      );
                    },
                    child: Container(
                      height: 50,
                      decoration: BoxDecoration(
                        color: AppTheme.primaryColor,
                        borderRadius: BorderRadius.circular(14),
                        boxShadow: [
                          BoxShadow(
                            color: AppTheme.primaryColor.withOpacity(0.22),
                            blurRadius: 10,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      alignment: Alignment.center,
                      child: const Text(
                        "Track Order",
                        style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white, fontSize: 15),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final totalItems = _cartService.totalMedicinesCount;
    final totalAmount = _cartService.grandTotal;
    final address = _cartService.selectedAddress;

    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      appBar: AppBar(
        title: const Text(
          "Checkout",
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: AppTheme.textColorPrimary),
        ),
        backgroundColor: Colors.transparent,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 18, color: AppTheme.textColorPrimary),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SafeArea(
        child: _isPlacingOrder
            ? _buildLoader()
            : Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Expanded(
                      child: SingleChildScrollView(
                        physics: const BouncingScrollPhysics(),
                        child: Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 8.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              // 1. Delivery Location Review
                              _buildSectionTitle("Delivery Address"),
                              const SizedBox(height: 10),
                              _buildAddressCard(address),
                              const SizedBox(height: 24),

                              // 2. Select Pharmacy Section
                              _buildSectionTitle("Select Pharmacy"),
                              const SizedBox(height: 10),
                              _buildSearchField(),
                              const SizedBox(height: 14),
                              _buildPharmacySelectionBlock(),
                              const SizedBox(height: 24),

                              // 3. Expanded Selected Pharmacy Details
                              if (_selectedPharmacy != null) ...[
                                _buildSelectedPharmacyDetailsCard(),
                                const SizedBox(height: 24),
                              ],

                              // 4. Delivery Instructions & Alternate Contact
                              _buildSectionTitle("Delivery Preferences"),
                              const SizedBox(height: 12),
                              _buildDeliveryPreferencesForm(),
                              const SizedBox(height: 24),

                              // 5. Order Summary
                              _buildSectionTitle("Order Summary"),
                              const SizedBox(height: 12),
                              _buildOrderSummaryCard(totalItems, totalAmount, address),
                              const SizedBox(height: 24),

                              // 6. Payment Method selection
                              _buildSectionTitle("Payment Method"),
                              const SizedBox(height: 12),
                              _buildPaymentMethodBlock(),
                              const SizedBox(height: 24),
                            ],
                          ),
                        ),
                      ),
                    ),

                    // Place Order Action Bar
                    _buildPlaceOrderActionBar(),
                  ],
                ),
              ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(
        fontSize: 16,
        fontWeight: FontWeight.bold,
        color: AppTheme.textColorPrimary,
        letterSpacing: -0.3,
      ),
    );
  }

  Widget _buildAddressCard(AddressModel? address) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.cardColor,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFFE5E7EB).withOpacity(0.5), width: 1),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.015),
            blurRadius: 12,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: AppTheme.secondaryColor.withOpacity(0.4),
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.location_on_outlined, color: AppTheme.primaryColor, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      address?.label ?? "Address",
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: AppTheme.textColorPrimary),
                    ),
                    const SizedBox(width: 8),
                    if (address?.pincode != null)
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
                        decoration: BoxDecoration(
                          color: AppTheme.secondaryColor,
                          borderRadius: BorderRadius.circular(6),
                          border: Border.all(color: AppTheme.primaryColor.withOpacity(0.15), width: 0.5),
                        ),
                        child: Text(
                          address!.pincode,
                          style: const TextStyle(color: AppTheme.primaryColor, fontSize: 10, fontWeight: FontWeight.bold),
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  address?.fullAddress ?? "No delivery address set",
                  style: const TextStyle(color: AppTheme.textColorSecondary, fontSize: 13, height: 1.35),
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          TextButton.icon(
            onPressed: _showAddressSelectionSheet,
            style: TextButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              backgroundColor: AppTheme.secondaryColor.withOpacity(0.3),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
            icon: const Icon(Icons.edit_location_alt_rounded, size: 16, color: AppTheme.primaryColor),
            label: const Text(
              "Change",
              style: TextStyle(color: AppTheme.primaryColor, fontWeight: FontWeight.bold, fontSize: 12),
            ),
          ),
        ],
      ),
    );
  }

  void _showAddressSelectionSheet() {
    final addresses = _profileService.getAddresses();

    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
      ),
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setSheetState) {
            return SafeArea(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(24, 16, 24, 24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Center(
                      child: Container(
                        width: 38,
                        height: 4,
                        margin: const EdgeInsets.only(bottom: 20),
                        decoration: BoxDecoration(
                          color: Colors.grey.shade300,
                          borderRadius: BorderRadius.circular(2),
                        ),
                      ),
                    ),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          "Select Delivery Address",
                          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: AppTheme.textColorPrimary),
                        ),
                        IconButton(
                          icon: const Icon(Icons.add_location_alt_outlined, color: AppTheme.primaryColor),
                          onPressed: () {
                            Navigator.pop(context);
                            _addNewAddressPrompt();
                          },
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    if (addresses.isEmpty)
                      const Padding(
                        padding: EdgeInsets.symmetric(vertical: 24),
                        child: Center(
                          child: Text("No addresses found. Add one to continue.", style: TextStyle(color: AppTheme.textColorSecondary)),
                        ),
                      )
                    else
                      Flexible(
                        child: ListView.builder(
                          shrinkWrap: true,
                          itemCount: addresses.length,
                          itemBuilder: (context, index) {
                            final addr = addresses[index];
                            final isSelected = _cartService.selectedAddress?.id == addr.id;

                            return Container(
                              margin: const EdgeInsets.only(bottom: 12),
                              decoration: BoxDecoration(
                                color: isSelected ? AppTheme.secondaryColor.withOpacity(0.2) : Colors.white,
                                borderRadius: BorderRadius.circular(16),
                                border: Border.all(
                                  color: isSelected ? AppTheme.primaryColor : Colors.grey.shade200,
                                  width: isSelected ? 1.5 : 1,
                                ),
                              ),
                              child: ListTile(
                                leading: Icon(
                                  addr.label.toLowerCase() == 'home' ? Icons.home_rounded : Icons.work_rounded,
                                  color: isSelected ? AppTheme.primaryColor : Colors.grey.shade500,
                                ),
                                title: Text(addr.label, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                                subtitle: Text("${addr.address}, ${addr.city} (${addr.pincode})", style: const TextStyle(fontSize: 12)),
                                trailing: isSelected ? const Icon(Icons.check_circle_rounded, color: AppTheme.primaryColor) : null,
                                onTap: () {
                                  _cartService.selectAddress(addr);
                                  _loadPharmacies(); // Re-sort pharmacies for this pincode
                                  Navigator.pop(context);
                                  setState(() {});
                                },
                              ),
                            );
                          },
                        ),
                      ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  void _addNewAddressPrompt() {
    final streetCtrl = TextEditingController();
    final cityCtrl = TextEditingController(text: "Bengaluru");
    final stateCtrl = TextEditingController(text: "Karnataka");
    final pincodeCtrl = TextEditingController(text: "560103");
    final formKey = GlobalKey<FormState>();

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          backgroundColor: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          title: const Text("Add Delivery Address", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
          content: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  TextFormField(
                    controller: streetCtrl,
                    decoration: const InputDecoration(labelText: "Flat / Street Address"),
                    validator: (v) => (v == null || v.trim().isEmpty) ? "Required" : null,
                  ),
                  const SizedBox(height: 10),
                  TextFormField(
                    controller: cityCtrl,
                    decoration: const InputDecoration(labelText: "City"),
                    validator: (v) => (v == null || v.trim().isEmpty) ? "Required" : null,
                  ),
                  const SizedBox(height: 10),
                  TextFormField(
                    controller: stateCtrl,
                    decoration: const InputDecoration(labelText: "State"),
                    validator: (v) => (v == null || v.trim().isEmpty) ? "Required" : null,
                  ),
                  const SizedBox(height: 10),
                  TextFormField(
                    controller: pincodeCtrl,
                    decoration: const InputDecoration(labelText: "Pincode"),
                    keyboardType: TextInputType.number,
                    validator: (v) => (v == null || v.trim().length != 6) ? "Enter 6-digit pincode" : null,
                  ),
                ],
              ),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text("Cancel"),
            ),
            ElevatedButton(
              onPressed: () async {
                if (formKey.currentState!.validate()) {
                  final newAddr = AddressModel(
                    id: DateTime.now().millisecondsSinceEpoch.toString(),
                    label: "Home",
                    address: streetCtrl.text.trim(),
                    city: cityCtrl.text.trim(),
                    state: stateCtrl.text.trim(),
                    pincode: pincodeCtrl.text.trim(),
                  );
                  await _profileService.addAddress(newAddr);
                  _cartService.selectAddress(newAddr);
                  await _loadPharmacies();
                  if (context.mounted) {
                    Navigator.pop(context);
                    setState(() {});
                  }
                }
              },
              child: const Text("Save & Select"),
            ),
          ],
        );
      },
    );
  }

  Widget _buildSearchField() {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.cardColor,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.015),
            blurRadius: 10,
            offset: const Offset(0, 4),
          )
        ],
      ),
      child: TextField(
        controller: _searchController,
        onChanged: _onSearchChanged,
        decoration: InputDecoration(
          hintText: "Search pharmacy, pharmacist, or location...",
          prefixIcon: const Icon(Icons.search_rounded, size: 20),
          suffixIcon: _searchQuery.isNotEmpty
              ? IconButton(
                  icon: const Icon(Icons.clear_rounded, size: 18),
                  onPressed: () {
                    _searchController.clear();
                    _onSearchChanged("");
                  },
                )
              : null,
        ),
      ),
    );
  }

  Widget _buildPharmacySelectionBlock() {
    if (_isLoadingPharmacies) {
      return _buildSkeletonLoader();
    }

    if (_pharmacies.isEmpty) {
      return _buildEmptyState();
    }

    if (_filteredPharmacies.isEmpty) {
      return _buildSearchEmptyState();
    }

    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: _filteredPharmacies.length,
      itemBuilder: (context, index) {
        final pharmacy = _filteredPharmacies[index];
        final isSelected = _selectedPharmacy?.pharmacyId == pharmacy.pharmacyId;

        return _buildPharmacySelectionCard(pharmacy, isSelected);
      },
    );
  }

  Widget _buildPharmacySelectionCard(PharmacyModel pharmacy, bool isSelected) {
    return AnimatedButtonWrapper(
      onPressed: () {
        setState(() {
          _selectedPharmacy = pharmacy;
        });
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(
            color: isSelected ? AppTheme.primaryColor : const Color(0xFFE5E7EB).withOpacity(0.5),
            width: isSelected ? 2 : 1,
          ),
          boxShadow: [
            BoxShadow(
              color: isSelected
                  ? AppTheme.primaryColor.withOpacity(0.03)
                  : Colors.black.withOpacity(0.015),
              blurRadius: 12,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Left icon container
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: pharmacy.isOpen
                    ? AppTheme.secondaryColor.withOpacity(0.4)
                    : Colors.red.shade50,
                borderRadius: BorderRadius.circular(14),
              ),
              child: Icon(
                Icons.local_pharmacy_rounded,
                color: pharmacy.isOpen ? AppTheme.primaryColor : Colors.red.shade400,
                size: 24,
              ),
            ),
            const SizedBox(width: 14),

            // Center details
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          pharmacy.pharmacyName,
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 14.5,
                            color: AppTheme.textColorPrimary,
                            letterSpacing: -0.2,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      // Rating badge
                      Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.star_rounded, color: Colors.amber, size: 16),
                          const SizedBox(width: 2),
                          Text(
                            pharmacy.rating.toString(),
                            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12.5, color: AppTheme.textColorPrimary),
                          ),
                        ],
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    "Pharmacist: ${pharmacy.pharmacistName}",
                    style: const TextStyle(color: AppTheme.textColorSecondary, fontSize: 12),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Icon(Icons.directions_run_rounded, size: 14, color: Colors.grey.shade400),
                      const SizedBox(width: 2),
                      Text(
                        pharmacy.distance,
                        style: TextStyle(fontSize: 11, color: AppTheme.textColorSecondary.withOpacity(0.8)),
                      ),
                      const SizedBox(width: 12),
                      Icon(Icons.schedule_rounded, size: 14, color: Colors.grey.shade400),
                      const SizedBox(width: 2),
                      Text(
                        pharmacy.deliveryTime,
                        style: TextStyle(fontSize: 11, color: AppTheme.textColorSecondary.withOpacity(0.9), fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  // Badges Row
                  Row(
                    children: [
                      // Open status
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(
                          color: pharmacy.isOpen ? Colors.green.shade50 : Colors.red.shade50,
                          borderRadius: BorderRadius.circular(6),
                          border: Border.all(color: pharmacy.isOpen ? Colors.green.shade100 : Colors.red.shade100, width: 0.5),
                        ),
                        child: Text(
                          pharmacy.isOpen ? "Open" : "Closed",
                          style: TextStyle(
                            color: pharmacy.isOpen ? Colors.green.shade800 : Colors.red.shade800,
                            fontWeight: FontWeight.bold,
                            fontSize: 10,
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),

                      // Availability badge
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(
                          color: pharmacy.availabilityStatus == "Available"
                              ? Colors.teal.shade50
                              : pharmacy.availabilityStatus == "Busy"
                                  ? Colors.amber.shade50
                                  : Colors.grey.shade100,
                          borderRadius: BorderRadius.circular(6),
                          border: Border.all(
                            color: pharmacy.availabilityStatus == "Available"
                                ? Colors.teal.shade100
                                : pharmacy.availabilityStatus == "Busy"
                                    ? Colors.amber.shade100
                                    : Colors.grey.shade200,
                            width: 0.5,
                          ),
                        ),
                        child: Text(
                          pharmacy.availabilityStatus,
                          style: TextStyle(
                            color: pharmacy.availabilityStatus == "Available"
                                ? Colors.teal.shade800
                                : pharmacy.availabilityStatus == "Busy"
                                    ? Colors.amber.shade800
                                    : Colors.grey.shade700,
                            fontWeight: FontWeight.bold,
                            fontSize: 10,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSelectedPharmacyDetailsCard() {
    final pharmacy = _selectedPharmacy!;
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppTheme.primaryColor.withOpacity(0.2), width: 1.2),
        boxShadow: [
          BoxShadow(
            color: AppTheme.primaryColor.withOpacity(0.015),
            blurRadius: 12,
            offset: const Offset(0, 6),
          )
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: AppTheme.primaryColor.withOpacity(0.12),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.check_circle_rounded, color: AppTheme.primaryColor, size: 16),
              ),
              const SizedBox(width: 8),
              const Text(
                "Selected Pharmacy Details",
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13.5, color: AppTheme.primaryColor),
              ),
            ],
          ),
          const Divider(height: 24, thickness: 0.5),

          Text(
            pharmacy.pharmacyName,
            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: AppTheme.textColorPrimary, letterSpacing: -0.2),
          ),
          const SizedBox(height: 14),

          _buildDetailRow("Pharmacist:", pharmacy.pharmacistName),
          _buildDetailRow("Registration No:", pharmacy.registrationNumber),
          _buildDetailRow("Contact:", pharmacy.phone),
          _buildDetailRow("Email:", pharmacy.email),
          _buildDetailRow("Address:", pharmacy.address),
          _buildDetailRow("Working Hours:", pharmacy.workingHours),
          _buildDetailRow("Estimated Delivery:", pharmacy.deliveryTime),

          const SizedBox(height: 12),
          const Text(
            "Available Services",
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: AppTheme.textColorPrimary),
          ),
          const SizedBox(height: 8),

          Wrap(
            spacing: 8,
            runSpacing: 6,
            children: pharmacy.availableServices.map((service) {
              return Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: AppTheme.primaryColor.withOpacity(0.05),
                  borderRadius: BorderRadius.circular(30),
                  border: Border.all(color: AppTheme.primaryColor.withOpacity(0.15), width: 0.5),
                ),
                child: Text(
                  service,
                  style: const TextStyle(
                    color: AppTheme.primaryColor,
                    fontSize: 10.5,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 130,
            child: Text(
              label,
              style: const TextStyle(color: AppTheme.textColorSecondary, fontSize: 12.5, fontWeight: FontWeight.w500),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(color: AppTheme.textColorPrimary, fontSize: 12.5, fontWeight: FontWeight.w600, height: 1.3),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDeliveryPreferencesForm() {
    return Column(
      children: [
        DropdownButtonFormField<String>(
          value: _selectedSlot,
          items: _slots.map((slot) {
            return DropdownMenuItem<String>(
              value: slot == "Earliest Available" ? "Earliest Available" : slot.split(" ").first,
              child: Text(slot),
            );
          }).toList(),
          onChanged: (val) {
            if (val != null) {
              setState(() {
                _selectedSlot = val;
              });
            }
          },
          decoration: const InputDecoration(
            labelText: "Delivery Slot Preference",
            prefixIcon: Icon(Icons.watch_later_outlined),
          ),
        ),
        const SizedBox(height: 16),

        TextFormField(
          controller: _altContactController,
          validator: _validateAltContact,
          keyboardType: TextInputType.phone,
          maxLength: 10,
          decoration: const InputDecoration(
            labelText: "Alternate Contact Number (Optional)",
            hintText: "Enter 10-digit mobile number",
            prefixIcon: Icon(Icons.phone_android_rounded),
            counterText: "",
          ),
        ),
        const SizedBox(height: 16),

        TextFormField(
          controller: _instructionsController,
          decoration: const InputDecoration(
            labelText: "Delivery Instructions (Optional)",
            hintText: "e.g., Leave at security gate, call before delivery",
            prefixIcon: Icon(Icons.directions_bike_rounded),
          ),
        ),
        const SizedBox(height: 16),

        TextFormField(
          controller: _notesController,
          maxLines: 3,
          decoration: const InputDecoration(
            labelText: "Order Notes (Optional)",
            hintText: "e.g., Deliver urgently, please avoid substitutions",
            prefixIcon: Icon(Icons.sticky_note_2_outlined),
          ),
        ),
      ],
    );
  }

  Widget _buildOrderSummaryCard(int totalItems, double totalAmount, AddressModel? address) {
    final hasPharmacy = _selectedPharmacy != null;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.cardColor,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFFE5E7EB).withOpacity(0.5), width: 1),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.015),
            blurRadius: 12,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        children: [
          _buildSummaryRow("Total Medicines", "$totalItems units"),
          const SizedBox(height: 8),
          _buildSummaryRow("Prescription Status", _cartService.prescriptionStatus),
          const SizedBox(height: 8),
          _buildSummaryRow("Selected Pharmacy", hasPharmacy ? _selectedPharmacy!.pharmacyName : "None Selected", isAccent: !hasPharmacy),
          const SizedBox(height: 8),
          _buildSummaryRow("Estimated Delivery Time", hasPharmacy ? _selectedPharmacy!.deliveryTime : "N/A"),
          const Divider(height: 24, thickness: 0.5),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                "Total Amount Payable",
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14.5, color: AppTheme.textColorPrimary),
              ),
              Text(
                "₹${totalAmount.toStringAsFixed(2)}",
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16.5, color: AppTheme.primaryColor),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryRow(String label, String value, {bool isAccent = false}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: const TextStyle(color: AppTheme.textColorSecondary, fontSize: 13, fontWeight: FontWeight.w500),
        ),
        Text(
          value,
          style: TextStyle(
            color: isAccent ? Colors.red.shade700 : AppTheme.textColorPrimary,
            fontWeight: FontWeight.w600,
            fontSize: 13,
          ),
        ),
      ],
    );
  }

  Widget _buildPaymentMethodBlock() {
    return Column(
      children: [
        // Cash on Delivery Card
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: AppTheme.primaryColor, width: 1.5),
            boxShadow: [
              BoxShadow(
                color: AppTheme.primaryColor.withOpacity(0.02),
                blurRadius: 10,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: const Row(
            children: [
              Checkbox(
                value: true,
                onChanged: null,
                activeColor: AppTheme.primaryColor,
              ),
              SizedBox(width: 8),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          "Cash on Delivery (COD)",
                          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14.5, color: AppTheme.textColorPrimary),
                        ),
                        SizedBox(width: 8),
                        Icon(Icons.payments_rounded, color: AppTheme.primaryColor, size: 18),
                      ],
                    ),
                    SizedBox(height: 2),
                    Text(
                      "Pay cash at your doorstep upon receiving order",
                      style: TextStyle(color: AppTheme.textColorSecondary, fontSize: 11.5),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Amber note card
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.amber.shade50,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: Colors.amber.shade200, width: 0.8),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(Icons.info_outline_rounded, color: Colors.amber.shade800, size: 20),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  "Please keep the exact amount ready during delivery.",
                  style: TextStyle(
                    color: Colors.amber.shade900,
                    fontSize: 12.5,
                    fontWeight: FontWeight.w500,
                    height: 1.35,
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildPlaceOrderActionBar() {
    final address = _cartService.selectedAddress;
    final blockCheckout = address == null || _pharmacies.isEmpty;

    return Container(
      padding: const EdgeInsets.fromLTRB(24, 16, 24, 28),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 16,
            offset: const Offset(0, -6),
          ),
        ],
        border: Border(top: BorderSide(color: Colors.grey.shade100, width: 1)),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text("Total Amount", style: TextStyle(color: AppTheme.textColorSecondary, fontSize: 12)),
                const SizedBox(height: 2),
                Text(
                  "₹${_cartService.grandTotal.toStringAsFixed(2)}",
                  style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppTheme.primaryColor, letterSpacing: -0.5),
                ),
              ],
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            flex: 2,
            child: AnimatedButtonWrapper(
              onPressed: blockCheckout ? null : _handlePlaceOrder,
              child: Container(
                height: 52,
                decoration: BoxDecoration(
                  color: blockCheckout ? Colors.grey.shade300 : AppTheme.primaryColor,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: blockCheckout
                      ? []
                      : [
                          BoxShadow(
                            color: AppTheme.primaryColor.withOpacity(0.22),
                            blurRadius: 10,
                            offset: const Offset(0, 4),
                          ),
                        ],
                ),
                alignment: Alignment.center,
                padding: const EdgeInsets.symmetric(horizontal: 10),
                child: FittedBox(
                  fit: BoxFit.scaleDown,
                  child: Text(
                    "Place Order",
                    style: TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.bold,
                      color: blockCheckout ? Colors.grey.shade600 : Colors.white,
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLoader() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const CircularProgressIndicator(
            valueColor: AlwaysStoppedAnimation<Color>(AppTheme.primaryColor),
            strokeWidth: 3.5,
          ),
          const SizedBox(height: 24),
          Text(
            "Placing Order...",
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: AppTheme.textColorPrimary,
                  letterSpacing: -0.5,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            "Securing order with pharmacy agent autopilot",
            style: TextStyle(color: AppTheme.textColorSecondary.withOpacity(0.9), fontSize: 13),
          ),
        ],
      ),
    );
  }

  Widget _buildSkeletonLoader() {
    return Column(
      children: List.generate(3, (index) {
        return Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.grey.shade50,
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: Colors.grey.shade100),
          ),
          child: Row(
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: Colors.grey.shade200,
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(width: 130, height: 12, color: Colors.grey.shade200),
                    const SizedBox(height: 8),
                    Container(width: 90, height: 9, color: Colors.grey.shade200),
                    const SizedBox(height: 6),
                    Container(width: 150, height: 9, color: Colors.grey.shade200),
                  ],
                ),
              ),
            ],
          ),
        );
      }),
    );
  }

  Widget _buildEmptyState() {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 28, horizontal: 16),
      decoration: BoxDecoration(
        color: Colors.red.shade50.withOpacity(0.25),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.red.shade100.withOpacity(0.4)),
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.red.shade50,
              shape: BoxShape.circle,
            ),
            child: Icon(Icons.local_pharmacy_outlined, color: Colors.red.shade800, size: 28),
          ),
          const SizedBox(height: 16),
          Text(
            "No pharmacy is currently available for your delivery location.",
            textAlign: TextAlign.center,
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13.5, color: Colors.red.shade900),
          ),
          const SizedBox(height: 6),
          Text(
            "Please try another address or try again later.",
            textAlign: TextAlign.center,
            style: TextStyle(color: AppTheme.textColorSecondary.withOpacity(0.95), fontSize: 12, height: 1.4),
          ),
        ],
      ),
    );
  }

  Widget _buildSearchEmptyState() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 28, horizontal: 16),
      decoration: BoxDecoration(
        color: AppTheme.cardColor,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        children: [
          Icon(Icons.search_off_rounded, color: Colors.grey.shade400, size: 36),
          const SizedBox(height: 12),
          const Text(
            "No matching pharmacy found",
            style: TextStyle(fontWeight: FontWeight.bold, color: AppTheme.textColorPrimary, fontSize: 14),
          ),
          const SizedBox(height: 6),
          Text(
            "Try searching by pharmacy name or pharmacist name instead.",
            textAlign: TextAlign.center,
            style: TextStyle(color: AppTheme.textColorSecondary.withOpacity(0.85), fontSize: 12),
          ),
        ],
      ),
    );
  }
}

// General button wrap that scales on press
class AnimatedButtonWrapper extends StatefulWidget {
  final VoidCallback? onPressed;
  final Widget child;

  const AnimatedButtonWrapper({
    super.key,
    required this.onPressed,
    required this.child,
  });

  @override
  State<AnimatedButtonWrapper> createState() => _AnimatedButtonWrapperState();
}

class _AnimatedButtonWrapperState extends State<AnimatedButtonWrapper>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scale;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 80),
    );
    _scale = Tween<double>(begin: 1.0, end: 0.96).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final bool isEnabled = widget.onPressed != null;
    return GestureDetector(
      onTapDown: isEnabled ? (_) => _controller.forward() : null,
      onTapUp: isEnabled ? (_) => _controller.reverse() : null,
      onTapCancel: isEnabled ? () => _controller.reverse() : null,
      onTap: widget.onPressed,
      child: AnimatedBuilder(
        animation: _scale,
        builder: (context, child) {
          return Transform.scale(
            scale: _scale.value,
            child: child,
          );
        },
        child: widget.child,
      ),
    );
  }
}
