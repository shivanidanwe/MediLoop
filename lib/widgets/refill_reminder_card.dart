import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import '../models/refill_model.dart';
import 'liquid_glass_card.dart';

class RefillReminderCard extends StatelessWidget {
  final RefillModel refill;
  final VoidCallback onReorder;

  const RefillReminderCard({
    super.key,
    required this.refill,
    required this.onReorder,
  });

  Color _getColorForPercentage(double pct) {
    if (pct >= 0.70) {
      return AppTheme.royalBlue;
    } else if (pct >= 0.40) {
      return AppTheme.warmYellow;
    } else {
      return AppTheme.coral;
    }
  }

  @override
  Widget build(BuildContext context) {
    final Color progressColor = _getColorForPercentage(refill.percentageRemaining);
    final String pctText = "${(refill.percentageRemaining * 100).toInt()}% In Stock";

    return LiquidGlassCard(
      borderRadius: 24,
      padding: const EdgeInsets.all(22),
      onTap: onReorder,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [progressColor, progressColor.withOpacity(0.7)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(
                      color: progressColor.withOpacity(0.3),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: const Center(
                  child: Icon(Icons.alarm_on_rounded, color: Colors.white, size: 24),
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      "Smart Refill Prediction",
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w800,
                        color: AppTheme.midnightNavy,
                        letterSpacing: -0.3,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      refill.medicineName,
                      style: const TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: AppTheme.royalBlue,
                      ),
                    ),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: progressColor.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: progressColor.withOpacity(0.3)),
                ),
                child: Text(
                  "${refill.daysRemaining} days left",
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w800,
                    color: progressColor,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // Linear Progress Bar
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: LinearProgressIndicator(
              value: refill.percentageRemaining.clamp(0.0, 1.0),
              backgroundColor: Colors.grey.shade100,
              valueColor: AlwaysStoppedAnimation<Color>(progressColor),
              minHeight: 8,
            ),
          ),
          const SizedBox(height: 12),

          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                pctText,
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                  color: AppTheme.textColorSecondary,
                ),
              ),
              GestureDetector(
                onTap: onReorder,
                child: const Row(
                  children: [
                    Text(
                      "Reorder Now",
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w800,
                        color: AppTheme.royalBlue,
                      ),
                    ),
                    SizedBox(width: 4),
                    Icon(Icons.arrow_forward_rounded, size: 14, color: AppTheme.royalBlue),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
