import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import '../models/address_model.dart';

class AddressCard extends StatelessWidget {
  final AddressModel address;
  final VoidCallback onEdit;
  final VoidCallback onDelete;
  final bool isDefault;

  const AddressCard({
    super.key,
    required this.address,
    required this.onEdit,
    required this.onDelete,
    this.isDefault = false,
  });

  IconData _getIconForLabel() {
    switch (address.label.toLowerCase()) {
      case 'home':
        return Icons.home_rounded;
      case 'office':
        return Icons.business_rounded;
      default:
        return Icons.location_on_rounded;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 8,
            offset: const Offset(0, 3),
          ),
        ],
        border: Border.all(
          color: isDefault ? AppTheme.primaryColor.withOpacity(0.3) : Colors.grey.shade100,
          width: isDefault ? 1.5 : 1,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Icon section
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: (isDefault ? AppTheme.primaryColor : Colors.grey.shade400).withOpacity(0.08),
                shape: BoxShape.circle,
              ),
              child: Icon(
                _getIconForLabel(),
                color: isDefault ? AppTheme.primaryColor : Colors.grey.shade600,
                size: 20,
              ),
            ),
            const SizedBox(width: 14),
            // Details section
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(
                        address.label,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 15,
                          color: AppTheme.textColorPrimary,
                        ),
                      ),
                      if (isDefault) ...[
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: AppTheme.primaryColor.withOpacity(0.12),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: const Text(
                            "Primary",
                            style: TextStyle(
                              color: AppTheme.primaryColor,
                              fontSize: 9,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ]
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text(
                    address.address,
                    style: TextStyle(
                      fontSize: 13,
                      height: 1.4,
                      color: Colors.grey.shade700,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    "${address.city}, ${address.state} - ${address.pincode}",
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                      color: Colors.grey.shade500,
                    ),
                  ),
                ],
              ),
            ),
            // Actions section
            Column(
              children: [
                IconButton(
                  icon: const Icon(Icons.edit_outlined, size: 18),
                  color: AppTheme.primaryColor,
                  constraints: const BoxConstraints(),
                  padding: const EdgeInsets.all(4),
                  onPressed: onEdit,
                  tooltip: "Edit Address",
                ),
                const SizedBox(height: 4),
                IconButton(
                  icon: const Icon(Icons.delete_outline_rounded, size: 18),
                  color: Colors.red.shade600,
                  constraints: const BoxConstraints(),
                  padding: const EdgeInsets.all(4),
                  onPressed: onDelete,
                  tooltip: "Delete Address",
                ),
              ],
            )
          ],
        ),
      ),
    );
  }
}
