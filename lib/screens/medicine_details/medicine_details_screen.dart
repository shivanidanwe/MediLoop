import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../models/medicine_model.dart';
import '../../services/cart_service.dart';

class MedicineDetailsScreen extends StatefulWidget {
  const MedicineDetailsScreen({super.key});

  @override
  State<MedicineDetailsScreen> createState() => _MedicineDetailsScreenState();
}

class _MedicineDetailsScreenState extends State<MedicineDetailsScreen> {
  int _quantity = 1;
  final CartService _cartService = CartService();

  @override
  Widget build(BuildContext context) {
    // Retrieve medicine from route arguments
    final Medicine? medicine = ModalRoute.of(context)?.settings.arguments as Medicine?;

    if (medicine == null) {
      return Scaffold(
        appBar: AppBar(title: const Text("Medicine Details")),
        body: const Center(
          child: Text("Error: No medicine details provided."),
        ),
      );
    }

    IconData dosageIcon;
    switch (medicine.dosageForm.toLowerCase()) {
      case 'tablet':
        dosageIcon = Icons.tablet_rounded;
        break;
      case 'syrup':
        dosageIcon = Icons.medication_liquid;
        break;
      case 'capsule':
        dosageIcon = Icons.medication_rounded;
        break;
      default:
        dosageIcon = Icons.medication_rounded;
    }

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: Text(
          medicine.name,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            letterSpacing: -0.5,
          ),
        ),
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: AppTheme.textColorPrimary,
        centerTitle: true,
        leading: Padding(
          padding: const EdgeInsets.all(8.0),
          child: Container(
            decoration: BoxDecoration(
              color: Colors.white,
              shape: BoxShape.circle,
              border: Border.all(
                color: const Color(0xFFE5E7EB),
                width: 1,
              ),
            ),
            child: IconButton(
              icon: const Icon(Icons.arrow_back_rounded, size: 18),
              onPressed: () => Navigator.pop(context),
              padding: EdgeInsets.zero,
              constraints: const BoxConstraints(),
            ),
          ),
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: SingleChildScrollView(
              physics: const BouncingScrollPhysics(),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Image/Icon Header Container (Premium Card View)
                  Container(
                     width: double.infinity,
                     height: 240,
                     margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                     decoration: BoxDecoration(
                       color: Colors.white,
                       borderRadius: BorderRadius.circular(24),
                       border: Border.all(
                         color: const Color(0xFFE5E7EB).withOpacity(0.6),
                         width: 1.2,
                       ),
                       boxShadow: [
                         BoxShadow(
                           color: Colors.black.withOpacity(0.015),
                           blurRadius: 16,
                           offset: const Offset(0, 6),
                         ),
                       ],
                     ),
                     child: Stack(
                       children: [
                         Positioned.fill(
                           child: Container(
                             decoration: BoxDecoration(
                               borderRadius: BorderRadius.circular(24),
                               gradient: LinearGradient(
                                 colors: [
                                   AppTheme.secondaryColor.withOpacity(0.05),
                                   AppTheme.primaryColor.withOpacity(0.02),
                                 ],
                                 begin: Alignment.topLeft,
                                 end: Alignment.bottomRight,
                               ),
                             ),
                           ),
                         ),
                         Center(
                           child: Hero(
                             tag: 'medicine-icon-${medicine.id}',
                             child: Icon(
                               dosageIcon,
                               size: 96,
                               color: AppTheme.primaryColor,
                             ),
                           ),
                         ),
                       ],
                     ),
                  ),

                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 24.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Badges Row
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                              decoration: BoxDecoration(
                                color: AppTheme.secondaryColor.withOpacity(0.4),
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(
                                  color: AppTheme.primaryColor.withOpacity(0.08),
                                  width: 1,
                                ),
                              ),
                              child: Text(
                                medicine.dosageForm.toUpperCase(),
                                style: const TextStyle(
                                  color: AppTheme.primaryColor,
                                  fontSize: 10,
                                  fontWeight: FontWeight.bold,
                                  letterSpacing: 0.5,
                                ),
                              ),
                            ),
                            const SizedBox(width: 8),
                            if (medicine.prescriptionRequired)
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                                decoration: BoxDecoration(
                                  color: AppTheme.secondaryColor,
                                  borderRadius: BorderRadius.circular(12),
                                  border: Border.all(
                                    color: AppTheme.primaryColor.withOpacity(0.2),
                                    width: 1,
                                  ),
                                ),
                                child: const Row(
                                  children: [
                                    Icon(
                                      Icons.description_outlined,
                                      color: AppTheme.primaryColor,
                                      size: 13,
                                    ),
                                    SizedBox(width: 4),
                                    Text(
                                      "Prescription Required",
                                      style: TextStyle(
                                        color: AppTheme.primaryColor,
                                        fontSize: 10,
                                        fontWeight: FontWeight.bold,
                                        letterSpacing: 0.2,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                          ],
                        ),
                        const SizedBox(height: 20),

                        // Title & Strength
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    medicine.name,
                                    style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                                          fontWeight: FontWeight.bold,
                                          color: AppTheme.textColorPrimary,
                                          letterSpacing: -0.8,
                                        ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    "Strength: ${medicine.strength}",
                                    style: const TextStyle(
                                      fontSize: 14,
                                      color: AppTheme.textColorSecondary,
                                      fontWeight: FontWeight.bold,
                                      letterSpacing: -0.2,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(width: 12),
                            Text(
                              "₹${medicine.price.toStringAsFixed(2)}",
                              style: const TextStyle(
                                fontSize: 26,
                                fontWeight: FontWeight.bold,
                                color: AppTheme.primaryColor,
                                letterSpacing: -0.8,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 10),

                        // Manufacturer
                        Text(
                          "Manufactured by ${medicine.manufacturer}",
                          style: TextStyle(
                            fontSize: 12,
                            color: AppTheme.textColorSecondary.withOpacity(0.8),
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 24),

                        // Description White Card
                        Container(
                          width: double.infinity,
                          padding: const EdgeInsets.all(20),
                          decoration: BoxDecoration(
                            color: AppTheme.cardColor,
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(
                              color: const Color(0xFFE5E7EB).withOpacity(0.6),
                              width: 1,
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withOpacity(0.01),
                                blurRadius: 10,
                                offset: const Offset(0, 4),
                              ),
                            ],
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Row(
                                children: [
                                  Icon(
                                    Icons.info_outline_rounded,
                                    color: AppTheme.primaryColor,
                                    size: 18,
                                  ),
                                  SizedBox(width: 8),
                                  Text(
                                    "Overview",
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 15,
                                      color: AppTheme.textColorPrimary,
                                      letterSpacing: -0.2,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 12),
                              const Divider(height: 1, color: Color(0xFFF3F4F6)),
                              const SizedBox(height: 12),
                              Text(
                                medicine.description,
                                style: const TextStyle(
                                  color: AppTheme.textColorSecondary,
                                  fontSize: 13,
                                  height: 1.6,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 24),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Bottom Bar with Qty Selector and CTA
          Container(
            padding: const EdgeInsets.fromLTRB(24, 16, 24, 24),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(28),
                topRight: Radius.circular(28),
              ),
              border: Border.all(
                color: const Color(0xFFE5E7EB).withOpacity(0.5),
                width: 1,
              ),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.03),
                  blurRadius: 20,
                  offset: const Offset(0, -6),
                ),
              ],
            ),
            child: Row(
              children: [
                // Qty Selector Pill
                SizedBox(
                  height: 54,
                  child: Container(
                    decoration: BoxDecoration(
                      color: const Color(0xFFF3F4F6),
                      borderRadius: BorderRadius.circular(27),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        IconButton(
                          icon: const Icon(Icons.remove_rounded, color: AppTheme.textColorPrimary, size: 18),
                          onPressed: () {
                            if (_quantity > 1) {
                              setState(() => _quantity--);
                            }
                          },
                        ),
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 4.0),
                          child: Text(
                            _quantity.toString(),
                            style: const TextStyle(
                              fontSize: 15,
                              fontWeight: FontWeight.bold,
                              color: AppTheme.textColorPrimary,
                            ),
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.add_rounded, color: AppTheme.textColorPrimary, size: 18),
                          onPressed: () {
                            setState(() => _quantity++);
                          },
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(width: 16),

                // CTA Button (Using primary Emerald Green from theme)
                Expanded(
                  child: ElevatedButton(
                    onPressed: () {
                      _cartService.addItem(medicine, quantity: _quantity);
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text('${medicine.name} ($_quantity) added to cart!'),
                          backgroundColor: AppTheme.primaryColor,
                          action: SnackBarAction(
                            label: 'View Cart',
                            textColor: Colors.white,
                            onPressed: () {
                              Navigator.pop(context);
                            },
                          ),
                        ),
                      );
                      Navigator.pop(context);
                    },
                    child: const Text("Add to Cart"),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
