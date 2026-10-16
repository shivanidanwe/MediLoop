import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../models/medicine_model.dart';
import '../../models/address_model.dart';
import '../../services/cart_service.dart';
import '../../services/profile_service.dart';
import '../../routes/app_routes.dart';

class CartScreen extends StatefulWidget {
  const CartScreen({super.key});

  @override
  State<CartScreen> createState() => _CartScreenState();
}

class _CartScreenState extends State<CartScreen> {
  final CartService _cartService = CartService();
  final ProfileService _profileService = ProfileService();

  @override
  void initState() {
    super.initState();
    _cartService.addListener(_onCartStateChanged);
    _profileService.addListener(_onProfileStateChanged);
    _syncDefaultAddress();
    _cartService.fetchCartFromBackend();
  }

  @override
  void dispose() {
    _cartService.removeListener(_onCartStateChanged);
    _profileService.removeListener(_onProfileStateChanged);
    super.dispose();
  }

  void _onCartStateChanged() {
    if (mounted) setState(() {});
  }

  void _onProfileStateChanged() {
    if (mounted) {
      _syncDefaultAddress();
      setState(() {});
    }
  }

  void _syncDefaultAddress() {
    if (_cartService.selectedAddress == null) {
      final addresses = _profileService.getAddresses();
      if (addresses.isNotEmpty) {
        // Set first address as default
        _cartService.selectAddress(addresses.first);
      }
    }
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
                    // Sheet Drag indicator
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
                        Text(
                          "Select Delivery Address",
                          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                fontWeight: FontWeight.bold,
                                color: AppTheme.textColorPrimary,
                                letterSpacing: -0.3,
                              ),
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
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 24),
                        child: Center(
                          child: Text(
                            "No addresses found. Add one to continue.",
                            style: TextStyle(color: AppTheme.textColorSecondary.withOpacity(0.8), fontSize: 13),
                          ),
                        ),
                      )
                    else
                      Flexible(
                        child: ListView.builder(
                          shrinkWrap: true,
                          physics: const BouncingScrollPhysics(),
                          itemCount: addresses.length,
                          itemBuilder: (context, index) {
                            final addr = addresses[index];
                            final isSelected = _cartService.selectedAddress?.id == addr.id;

                            return Container(
                              margin: const EdgeInsets.only(bottom: 12),
                              decoration: BoxDecoration(
                                color: isSelected ? AppTheme.secondaryColor.withOpacity(0.2) : Colors.white,
                                borderRadius: BorderRadius.circular(20),
                                border: Border.all(
                                  color: isSelected ? AppTheme.primaryColor : Colors.grey.shade200,
                                  width: isSelected ? 1.5 : 1,
                                ),
                              ),
                              child: ListTile(
                                leading: Container(
                                  padding: const EdgeInsets.all(8),
                                  decoration: BoxDecoration(
                                    color: isSelected ? AppTheme.secondaryColor : Colors.grey.shade100,
                                    shape: BoxShape.circle,
                                  ),
                                  child: Icon(
                                    addr.label.toLowerCase() == 'home'
                                        ? Icons.home_rounded
                                        : addr.label.toLowerCase() == 'office'
                                            ? Icons.work_rounded
                                            : Icons.location_on_rounded,
                                    color: isSelected ? AppTheme.primaryColor : AppTheme.textColorSecondary,
                                    size: 20,
                                  ),
                                ),
                                title: Text(
                                  addr.label,
                                  style: const TextStyle(
                                    fontWeight: FontWeight.bold,
                                    fontSize: 14,
                                    color: AppTheme.textColorPrimary,
                                  ),
                                ),
                                subtitle: Text(
                                  addr.fullAddress,
                                  style: const TextStyle(fontSize: 12, color: AppTheme.textColorSecondary),
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
                                trailing: isSelected
                                    ? const Icon(Icons.check_circle_rounded, color: AppTheme.primaryColor)
                                    : null,
                                onTap: () {
                                  _cartService.selectAddress(addr);
                                  Navigator.pop(context);
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
    final formKey = GlobalKey<FormState>();
    final streetCtrl = TextEditingController();
    final cityCtrl = TextEditingController();
    final stateCtrl = TextEditingController();
    final pincodeCtrl = TextEditingController();
    String label = 'Home';

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          backgroundColor: Colors.white,
          surfaceTintColor: Colors.transparent,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
          title: const Text(
            "Add New Address",
            style: TextStyle(fontWeight: FontWeight.bold, color: AppTheme.textColorPrimary, letterSpacing: -0.3),
          ),
          content: SingleChildScrollView(
            child: Form(
              key: formKey,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  DropdownButtonFormField<String>(
                    value: label,
                    items: ['Home', 'Office', 'Other'].map((l) {
                      return DropdownMenuItem(value: l, child: Text(l));
                    }).toList(),
                    onChanged: (val) => label = val ?? 'Home',
                    decoration: const InputDecoration(labelText: "Label"),
                  ),
                  const SizedBox(height: 14),
                  TextFormField(
                    controller: streetCtrl,
                    decoration: const InputDecoration(labelText: "Street Address"),
                    validator: (val) => val == null || val.trim().isEmpty ? "Required" : null,
                  ),
                  const SizedBox(height: 14),
                  TextFormField(
                    controller: cityCtrl,
                    decoration: const InputDecoration(labelText: "City"),
                    validator: (val) => val == null || val.trim().isEmpty ? "Required" : null,
                  ),
                  const SizedBox(height: 14),
                  Row(
                    children: [
                      Expanded(
                        child: TextFormField(
                          controller: stateCtrl,
                          decoration: const InputDecoration(labelText: "State"),
                          validator: (val) => val == null || val.trim().isEmpty ? "Required" : null,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: TextFormField(
                          controller: pincodeCtrl,
                          keyboardType: TextInputType.number,
                          decoration: const InputDecoration(labelText: "Pincode"),
                          validator: (val) => val == null || val.trim().length != 6 ? "6 digits" : null,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text("Cancel", style: TextStyle(color: AppTheme.textColorSecondary, fontWeight: FontWeight.bold)),
            ),
            ElevatedButton(
              onPressed: () {
                if (formKey.currentState!.validate()) {
                  final newAddr = AddressModel(
                    id: DateTime.now().millisecondsSinceEpoch.toString(),
                    label: label,
                    address: streetCtrl.text.trim(),
                    city: cityCtrl.text.trim(),
                    state: stateCtrl.text.trim(),
                    pincode: pincodeCtrl.text.trim(),
                  );
                  _profileService.addAddress(newAddr);
                  _cartService.selectAddress(newAddr);
                  Navigator.pop(context);
                }
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.primaryColor,
                minimumSize: const Size(100, 44),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              child: const Text("Save"),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final cartItems = _cartService.items;

    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      appBar: AppBar(
        title: Column(
          children: [
            const Text(
              "My Cart",
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: AppTheme.textColorPrimary),
            ),
            if (cartItems.isNotEmpty) ...[
              const SizedBox(height: 2),
              Text(
                "${_cartService.totalMedicinesCount} ${_cartService.totalMedicinesCount == 1 ? 'item' : 'items'} in your cart",
                style: const TextStyle(fontSize: 12, color: AppTheme.textColorSecondary),
              ),
            ],
          ],
        ),
        backgroundColor: Colors.transparent,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
      ),
      body: SafeArea(
        child: cartItems.isEmpty
            ? _buildEmptyState()
            : Column(
                children: [
                  Expanded(
                    child: SingleChildScrollView(
                      physics: const BouncingScrollPhysics(),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // 1. Prescription Required Warnings & Status
                          if (_cartService.requiresPrescription) _buildPrescriptionStatusSection(),

                          // 2. Cart Items list
                          ListView.builder(
                            shrinkWrap: true,
                            physics: const NeverScrollableScrollPhysics(),
                            itemCount: cartItems.length,
                            itemBuilder: (context, index) {
                              return _buildCartItemCard(cartItems[index]);
                            },
                          ),

                          // 3. Delivery Address Section
                          _buildDeliveryAddressSection(),

                          // 4. Order Summary panel
                          _buildOrderSummarySection(),
                          const SizedBox(height: 24),
                        ],
                      ),
                    ),
                  ),

                  // Checkout Floating Bar
                  _buildCheckoutBar(),
                ],
              ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 40.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Empty State Illustration
            TweenAnimationBuilder<double>(
              tween: Tween(begin: 0.0, end: 1.0),
              duration: const Duration(milliseconds: 700),
              curve: Curves.easeOutCubic,
              builder: (context, value, child) {
                return Opacity(
                  opacity: value,
                  child: Transform.scale(
                    scale: 0.88 + (value * 0.12),
                    child: child,
                  ),
                );
              },
              child: SizedBox(
                width: 170,
                height: 170,
                child: CustomPaint(
                  painter: CartEmptyIllustrationPainter(
                    primaryColor: AppTheme.primaryColor,
                    secondaryColor: AppTheme.secondaryColor,
                    accentColor: AppTheme.accentColor,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 28),
            const Text(
              "Your Cart is Empty",
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 20,
                color: AppTheme.textColorPrimary,
                letterSpacing: -0.5,
              ),
            ),
            const SizedBox(height: 10),
            Text(
              "Medicines added to your cart will appear here. Search and find medicines to get started.",
              textAlign: TextAlign.center,
              style: TextStyle(
                color: AppTheme.textColorSecondary.withOpacity(0.9),
                fontSize: 13.5,
                height: 1.45,
              ),
            ),
            const SizedBox(height: 36),
            AnimatedButtonWrapper(
              onPressed: () {
                Navigator.pushNamed(context, AppRoutes.searchMedicines);
              },
              child: Container(
                width: 190,
                height: 52,
                decoration: BoxDecoration(
                  color: AppTheme.primaryColor,
                  borderRadius: BorderRadius.circular(16),
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
                  "Browse Medicines",
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 15,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPrescriptionStatusSection() {
    final status = _cartService.prescriptionStatus;
    Color statusColor;
    IconData statusIcon;
    String statusText;

    switch (status) {
      case 'Uploaded':
        statusColor = Colors.blue.shade800;
        statusIcon = Icons.cloud_done_outlined;
        statusText = "Prescription Uploaded";
        break;
      case 'Verification Pending':
        statusColor = Colors.orange.shade800;
        statusIcon = Icons.hourglass_empty_rounded;
        statusText = "Verification Pending";
        break;
      case 'Verified':
        statusColor = AppTheme.primaryColor;
        statusIcon = Icons.verified_rounded;
        statusText = "Prescription Verified";
        break;
      default:
        statusColor = Colors.red.shade800;
        statusIcon = Icons.warning_amber_rounded;
        statusText = "Upload Prescription to continue";
    }

    final isWarning = status == "None";

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isWarning ? Colors.red.shade50 : statusColor.withOpacity(0.06),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: isWarning ? Colors.red.shade200 : statusColor.withOpacity(0.2),
          width: 1,
        ),
      ),
      child: Row(
        children: [
          Icon(statusIcon, color: isWarning ? Colors.red.shade800 : statusColor, size: 24),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  isWarning ? "⚠ $statusText" : statusText,
                  style: TextStyle(
                    color: isWarning ? Colors.red.shade900 : statusColor,
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  isWarning
                      ? "Some medicines in your cart require a valid prescription."
                      : status == 'Verified'
                          ? "Verification complete. Proceed to checkout."
                          : "Our pharmacy team is verifying your upload.",
                  style: TextStyle(
                    color: isWarning ? Colors.red.shade700 : AppTheme.textColorSecondary,
                    fontSize: 11.5,
                  ),
                ),
              ],
            ),
          ),
          if (isWarning) ...[
            const SizedBox(width: 12),
            AnimatedButtonWrapper(
              onPressed: () {
                Navigator.pushNamed(context, AppRoutes.uploadPrescription);
              },
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                decoration: BoxDecoration(
                  color: Colors.red.shade800,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Text(
                  "Upload",
                  style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildCartItemCard(CartItem item) {
    final med = item.medicine;
    IconData dosageIcon;
    switch (med.dosageForm.toLowerCase()) {
      case 'tablet':
        dosageIcon = Icons.tablet_rounded;
        break;
      case 'syrup':
        dosageIcon = Icons.medication_liquid_rounded;
        break;
      default:
        dosageIcon = Icons.medication_rounded;
    }

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 15,
            offset: const Offset(0, 6),
          ),
        ],
        border: Border.all(color: const Color(0xFFE5E7EB).withOpacity(0.5), width: 1),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Styled Icon Box
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              color: AppTheme.secondaryColor.withOpacity(0.4),
              borderRadius: BorderRadius.circular(14),
            ),
            child: Icon(dosageIcon, color: AppTheme.primaryColor, size: 26),
          ),
          const SizedBox(width: 14),

          // Detail column
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Text(
                        med.name,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 15.5,
                          color: AppTheme.textColorPrimary,
                          letterSpacing: -0.3,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    const SizedBox(width: 8),
                    GestureDetector(
                      onTap: () => _cartService.removeItem(med.id),
                      child: const Icon(
                        Icons.delete_outline_rounded,
                        color: Colors.grey,
                        size: 20,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 2),
                Text(
                  "${med.dosageForm} • ${med.strength}",
                  style: const TextStyle(color: AppTheme.textColorSecondary, fontSize: 12),
                ),
                const SizedBox(height: 8),
                if (med.prescriptionRequired)
                  Container(
                    margin: const EdgeInsets.only(bottom: 10),
                    padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
                    decoration: BoxDecoration(
                      color: AppTheme.secondaryColor.withOpacity(0.3),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: AppTheme.primaryColor.withOpacity(0.2), width: 0.5),
                    ),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.assignment_late_rounded, color: AppTheme.primaryColor, size: 10),
                        SizedBox(width: 4),
                        Text(
                          "Prescription Required",
                          style: TextStyle(color: AppTheme.primaryColor, fontSize: 9.5, fontWeight: FontWeight.bold),
                        ),
                      ],
                    ),
                  ),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      "₹${med.price.toStringAsFixed(2)} / unit",
                      style: TextStyle(color: AppTheme.textColorSecondary.withOpacity(0.9), fontSize: 12.5),
                    ),
                    Text(
                      "Total: ₹${item.totalPrice.toStringAsFixed(2)}",
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14.5, color: AppTheme.textColorPrimary),
                    ),
                  ],
                ),
                const SizedBox(height: 12),

                // Qty Selector
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    Container(
                      height: 34,
                      decoration: BoxDecoration(
                        color: AppTheme.backgroundColor,
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: Colors.grey.shade200),
                      ),
                      child: Row(
                        children: [
                          AnimatedButtonWrapper(
                            onPressed: () => _cartService.updateQuantity(med.id, -1),
                            child: const SizedBox(
                              width: 34,
                              height: 34,
                              child: Icon(Icons.remove_rounded, size: 14, color: AppTheme.textColorPrimary),
                            ),
                          ),
                          Container(
                            alignment: Alignment.center,
                            padding: const EdgeInsets.symmetric(horizontal: 10.0),
                            child: Text(
                              item.quantity.toString(),
                              style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppTheme.textColorPrimary),
                            ),
                          ),
                          AnimatedButtonWrapper(
                            onPressed: () => _cartService.updateQuantity(med.id, 1),
                            child: const SizedBox(
                              width: 34,
                              height: 34,
                              child: Icon(Icons.add_rounded, size: 14, color: AppTheme.textColorPrimary),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDeliveryAddressSection() {
    final selectedAddress = _cartService.selectedAddress;

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.cardColor,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFFE5E7EB).withOpacity(0.5), width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Row(
                children: [
                  Icon(Icons.local_shipping_outlined, color: AppTheme.primaryColor, size: 20),
                  SizedBox(width: 8),
                  Text(
                    "Delivery Address",
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14.5, color: AppTheme.textColorPrimary),
                  ),
                ],
              ),
              TextButton(
                onPressed: _showAddressSelectionSheet,
                style: TextButton.styleFrom(padding: EdgeInsets.zero, minimumSize: const Size(0, 0)),
                child: const Text(
                  "Change Address",
                  style: TextStyle(color: AppTheme.primaryColor, fontWeight: FontWeight.bold, fontSize: 12.5),
                ),
              ),
            ],
          ),
          const Divider(height: 16, thickness: 0.5),
          if (selectedAddress == null)
            Row(
              children: [
                Expanded(
                  child: Text(
                    "No delivery address selected. Please add or select an address.",
                    style: TextStyle(color: Colors.red.shade700, fontSize: 13, fontWeight: FontWeight.w500),
                  ),
                ),
              ],
            )
          else
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppTheme.secondaryColor.withOpacity(0.4),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: AppTheme.primaryColor.withOpacity(0.15), width: 0.5),
                  ),
                  child: Text(
                    selectedAddress.label,
                    style: const TextStyle(color: AppTheme.primaryColor, fontSize: 10.5, fontWeight: FontWeight.bold),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    selectedAddress.fullAddress,
                    style: const TextStyle(color: AppTheme.textColorSecondary, fontSize: 13, height: 1.35),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
        ],
      ),
    );
  }

  Widget _buildOrderSummarySection() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.cardColor,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFFE5E7EB).withOpacity(0.5), width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "Order Summary",
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14.5, color: AppTheme.textColorPrimary),
          ),
          const Divider(height: 20, thickness: 0.5),
          _buildSummaryRow("Total Medicines", "${_cartService.totalMedicinesCount} items"),
          const SizedBox(height: 8),
          _buildSummaryRow("Subtotal", "₹${_cartService.subtotal.toStringAsFixed(2)}"),
          const SizedBox(height: 8),
          _buildSummaryRow(
            "Delivery Charges",
            _cartService.deliveryCharges == 0.0 ? "FREE" : "₹${_cartService.deliveryCharges.toStringAsFixed(2)}",
            isPromo: _cartService.deliveryCharges == 0.0,
          ),
          const SizedBox(height: 8),
          if (_cartService.discount > 0) ...[
            _buildSummaryRow("Discount (Promo)", "-₹${_cartService.discount.toStringAsFixed(2)}", isPromo: true),
            const SizedBox(height: 8),
          ],
          const Divider(height: 24, thickness: 0.5),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                "Grand Total",
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15.5, color: AppTheme.textColorPrimary),
              ),
              Text(
                "₹${_cartService.grandTotal.toStringAsFixed(2)}",
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: AppTheme.primaryColor),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryRow(String label, String value, {bool isPromo = false}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: const TextStyle(color: AppTheme.textColorSecondary, fontSize: 13),
        ),
        Text(
          value,
          style: TextStyle(
            color: isPromo ? AppTheme.primaryColor : AppTheme.textColorPrimary,
            fontWeight: isPromo ? FontWeight.bold : FontWeight.w600,
            fontSize: 13,
          ),
        ),
      ],
    );
  }

  Widget _buildCheckoutBar() {
    final blockCheckout = _cartService.items.isEmpty ||
        _cartService.selectedAddress == null ||
        _cartService.hasPrescriptionWarning;

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
                const Text("Total Payable", style: TextStyle(color: AppTheme.textColorSecondary, fontSize: 12)),
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
              onPressed: blockCheckout
                  ? null
                  : () {
                      Navigator.pushNamed(context, AppRoutes.payment);
                    },
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
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      "Proceed to Payment",
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                        color: blockCheckout ? Colors.grey.shade600 : Colors.white,
                      ),
                    ),
                    const SizedBox(width: 6),
                    Icon(
                      Icons.arrow_forward_rounded,
                      size: 16,
                      color: blockCheckout ? Colors.grey.shade600 : Colors.white,
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// Custom button scale wrapper
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

// Custom Painter drawing the empty cart state illustration
class CartEmptyIllustrationPainter extends CustomPainter {
  final Color primaryColor;
  final Color secondaryColor;
  final Color accentColor;

  CartEmptyIllustrationPainter({
    required this.primaryColor,
    required this.secondaryColor,
    required this.accentColor,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final width = size.width;
    final height = size.height;
    final center = Offset(width / 2, height / 2);

    // 1. Soft background circle
    final bgPaint = Paint()
      ..color = secondaryColor.withOpacity(0.35)
      ..style = PaintingStyle.fill;
    canvas.drawCircle(center, width * 0.42, bgPaint);

    // 2. Decorative dashed border
    final dotPaint = Paint()
      ..color = primaryColor.withOpacity(0.18)
      ..strokeWidth = 1.5
      ..style = PaintingStyle.stroke;

    final double radius = width * 0.46;
    const int dashCount = 36;
    for (int i = 0; i < dashCount; i++) {
      final double angle = (i * 2 * 3.141592653589793) / dashCount;
      final double nextAngle = ((i + 0.5) * 2 * 3.141592653589793) / dashCount;
      canvas.drawArc(
        Rect.fromCircle(center: center, radius: radius),
        angle,
        nextAngle - angle,
        false,
        dotPaint,
      );
    }

    // 3. Draw Basket Outline
    final basketPaint = Paint()
      ..color = primaryColor
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    final basketFill = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.fill;

    final basketPath = Path();
    final double bWidth = width * 0.46;
    final double bHeight = height * 0.28;
    final double topY = center.dy - bHeight * 0.1;
    final double bottomY = center.dy + bHeight * 0.8;

    basketPath.moveTo(center.dx - bWidth * 0.5, topY);
    basketPath.lineTo(center.dx + bWidth * 0.5, topY);
    basketPath.lineTo(center.dx + bWidth * 0.38, bottomY);
    basketPath.quadraticBezierTo(
      center.dx + bWidth * 0.35, bottomY + bHeight * 0.15,
      center.dx + bWidth * 0.25, bottomY + bHeight * 0.15,
    );
    basketPath.lineTo(center.dx - bWidth * 0.25, bottomY + bHeight * 0.15);
    basketPath.quadraticBezierTo(
      center.dx - bWidth * 0.35, bottomY + bHeight * 0.15,
      center.dx - bWidth * 0.38, bottomY,
    );
    basketPath.close();

    final shadowPaint = Paint()
      ..color = Colors.black.withOpacity(0.04)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 6);
    canvas.drawPath(basketPath.shift(const Offset(0, 4)), shadowPaint);
    canvas.drawPath(basketPath, basketFill);
    canvas.drawPath(basketPath, basketPaint);

    canvas.drawLine(
      Offset(center.dx - bWidth * 0.52, topY),
      Offset(center.dx + bWidth * 0.52, topY),
      Paint()..color = primaryColor..strokeWidth = 4..strokeCap = StrokeCap.round,
    );

    final strutPaint = Paint()
      ..color = primaryColor.withOpacity(0.4)
      ..strokeWidth = 2
      ..strokeCap = StrokeCap.round;
    
    canvas.drawLine(Offset(center.dx - bWidth * 0.44, topY + bHeight * 0.3), Offset(center.dx + bWidth * 0.44, topY + bHeight * 0.3), strutPaint);
    canvas.drawLine(Offset(center.dx - bWidth * 0.40, topY + bHeight * 0.6), Offset(center.dx + bWidth * 0.40, topY + bHeight * 0.6), strutPaint);

    canvas.drawLine(Offset(center.dx - bWidth * 0.2, topY), Offset(center.dx - bWidth * 0.16, bottomY), strutPaint);
    canvas.drawLine(Offset(center.dx, topY), Offset(center.dx, bottomY), strutPaint);
    canvas.drawLine(Offset(center.dx + bWidth * 0.2, topY), Offset(center.dx + bWidth * 0.16, bottomY), strutPaint);

    final handlePaint = Paint()
      ..color = primaryColor.withOpacity(0.8)
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;
    
    canvas.drawArc(
      Rect.fromCenter(center: Offset(center.dx, topY), width: bWidth * 0.8, height: bHeight * 0.8),
      3.141592653589793,
      3.141592653589793,
      false,
      handlePaint,
    );

    // 5. Floating badge (left)
    canvas.save();
    canvas.translate(center.dx - bWidth * 0.55, center.dy - bHeight * 0.55);
    final badgePaint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.fill;
    final badgeShadow = Paint()
      ..color = Colors.black.withOpacity(0.04)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 3);
    canvas.drawCircle(const Offset(0, 1), 10, badgeShadow);
    canvas.drawCircle(Offset.zero, 10, badgePaint);

    final plusPaint = Paint()
      ..color = primaryColor
      ..strokeWidth = 2
      ..strokeCap = StrokeCap.round;
    canvas.drawLine(const Offset(-4, 0), const Offset(4, 0), plusPaint);
    canvas.drawLine(const Offset(0, -4), const Offset(0, 4), plusPaint);
    canvas.restore();

    // Floating Capsule (top right)
    canvas.save();
    canvas.translate(center.dx + bWidth * 0.45, center.dy - bHeight * 0.45);
    canvas.rotate(0.5);
    
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromCenter(center: const Offset(0, 1), width: 10, height: 20),
        const Radius.circular(5),
      ),
      Paint()..color = Colors.black.withOpacity(0.04)..maskFilter = const MaskFilter.blur(BlurStyle.normal, 2),
    );

    final pillRectBottom = RRect.fromRectAndCorners(
      const Rect.fromLTWH(-5, 0, 10, 10),
      bottomLeft: const Radius.circular(5),
      bottomRight: const Radius.circular(5),
    );
    final pillRectTop = RRect.fromRectAndCorners(
      const Rect.fromLTWH(-5, -10, 10, 10),
      topLeft: const Radius.circular(5),
      topRight: const Radius.circular(5),
    );

    canvas.drawRRect(pillRectTop, Paint()..color = accentColor);
    canvas.drawRRect(pillRectBottom, Paint()..color = secondaryColor);

    canvas.drawLine(
      const Offset(-5, 0),
      const Offset(5, 0),
      Paint()..color = Colors.white..strokeWidth = 1,
    );
    canvas.restore();

    final sparkPaint = Paint()
      ..color = accentColor
      ..style = PaintingStyle.fill;
    _drawSparkle(canvas, center.translate(-width * 0.32, -height * 0.2), 5, sparkPaint);
    _drawSparkle(canvas, center.translate(width * 0.32, height * 0.28), 6, sparkPaint);
  }

  void _drawSparkle(Canvas canvas, Offset offset, double size, Paint paint) {
    final path = Path();
    path.moveTo(offset.dx, offset.dy - size);
    path.quadraticBezierTo(offset.dx, offset.dy, offset.dx + size, offset.dy);
    path.quadraticBezierTo(offset.dx, offset.dy, offset.dx, offset.dy + size);
    path.quadraticBezierTo(offset.dx, offset.dy, offset.dx - size, offset.dy);
    path.quadraticBezierTo(offset.dx, offset.dy, offset.dx, offset.dy - size);
    path.close();
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CartEmptyIllustrationPainter oldDelegate) {
    return oldDelegate.primaryColor != primaryColor ||
        oldDelegate.secondaryColor != secondaryColor ||
        oldDelegate.accentColor != accentColor;
  }
}
