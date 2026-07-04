import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import '../models/medicine_model.dart';

class CategoryCard extends StatelessWidget {
  final Category category;
  final VoidCallback onTap;

  const CategoryCard({
    super.key,
    required this.category,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 80,
        margin: const EdgeInsets.only(right: 12),
        child: Column(
          children: [
            Container(
              height: 60,
              width: 60,
              decoration: BoxDecoration(
                color: AppTheme.primaryColor.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                _getIconData(category.iconPath),
                color: AppTheme.primaryColor,
                size: 28,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              category.name,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w500,
                color: AppTheme.textColorPrimary,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }

  IconData _getIconData(String path) {
    switch (path) {
      case 'tablet': return Icons.tablet_rounded;
      case 'medication': return Icons.medication;
      case 'medication_liquid': return Icons.medication_liquid;
      case 'health_and_safety': return Icons.health_and_safety;
      case 'child_care': return Icons.child_care;
      case 'face': return Icons.face;
      case 'medical_information': return Icons.medical_information;
      case 'bloodtype': return Icons.bloodtype;
      default: return Icons.category;
    }
  }
}
