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
        width: 82,
        margin: const EdgeInsets.only(right: 12),
        child: Column(
          children: [
            Container(
              height: 60,
              width: 60,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    AppTheme.royalBlue.withOpacity(0.1),
                    AppTheme.electricCyan.withOpacity(0.08),
                  ],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: Colors.white,
                  width: 1.5,
                ),
                boxShadow: [
                  BoxShadow(
                    color: AppTheme.midnightNavy.withOpacity(0.04),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Center(
                child: Icon(
                  _getIconData(category.iconPath),
                  color: AppTheme.royalBlue,
                  size: 26,
                ),
              ),
            ),
            const SizedBox(height: 7),
            Text(
              category.name,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w700,
                color: AppTheme.midnightNavy,
                letterSpacing: -0.1,
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
    if (path.contains('prescription')) return Icons.receipt_long_rounded;
    if (path.contains('otc')) return Icons.medication_rounded;
    if (path.contains('wellness')) return Icons.spa_rounded;
    if (path.contains('personal')) return Icons.clean_hands_rounded;
    if (path.contains('baby')) return Icons.child_care_rounded;
    if (path.contains('cardiac')) return Icons.favorite_rounded;
    if (path.contains('diabetic')) return Icons.bloodtype_rounded;
    return Icons.medical_services_rounded;
  }
}
