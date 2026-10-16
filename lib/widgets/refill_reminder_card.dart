import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import '../models/refill_model.dart';

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
      return AppTheme.primaryColor; // Green
    } else if (pct >= 0.40) {
      return Colors.amber.shade700; // Yellow/Amber
    } else if (pct >= 0.20) {
      return Colors.orange.shade800; // Orange
    } else {
      return Colors.red.shade700; // Red
    }
  }

  @override
  Widget build(BuildContext context) {
    final Color progressColor = _getColorForPercentage(refill.percentageRemaining);
    final String pctText = "${(refill.percentageRemaining * 100).toInt()}% Remaining";

    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: AppTheme.cardColor,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(
          color: const Color(0xFFE5E7EB).withOpacity(0.5),
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 16,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(24),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: onReorder,
            child: Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Card Header
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: AppTheme.primaryColor.withOpacity(0.08),
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(
                          Icons.notifications_active_outlined,
                          color: AppTheme.primaryColor,
                          size: 18,
                        ),
                      ),
                      const SizedBox(width: 10),
                      Text(
                        "AI Refill Reminder",
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              color: AppTheme.primaryColor,
                              fontWeight: FontWeight.bold,
                              fontSize: 15,
                            ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 18),

                  // Medicine Info
                  Text(
                    refill.medicineName,
                    style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: AppTheme.textColorPrimary,
                          letterSpacing: -0.3,
                        ),
                  ),
                  const SizedBox(height: 6),
                  Row(
                    children: [
                      Text(
                        "Estimated stock level: ",
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: AppTheme.textColorSecondary,
                            ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: progressColor.withOpacity(0.08),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(
                            color: progressColor.withOpacity(0.15),
                            width: 1,
                          ),
                        ),
                        child: Text(
                          "${refill.daysRemaining} Days left",
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: progressColor,
                                fontWeight: FontWeight.bold,
                                fontSize: 13,
                              ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),

                  // Progress Bar Title/Info
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        "Stock Status",
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: AppTheme.textColorSecondary.withOpacity(0.8),
                              fontWeight: FontWeight.bold,
                              letterSpacing: 0.2,
                            ),
                      ),
                      Text(
                        pctText,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: progressColor,
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),

                  // Animated Progress Bar
                  TweenAnimationBuilder<double>(
                    tween: Tween<double>(begin: 0, end: refill.percentageRemaining),
                    duration: const Duration(milliseconds: 1000),
                    curve: Curves.easeOutCubic,
                    builder: (context, value, child) {
                      return Stack(
                        children: [
                          Container(
                            height: 12,
                            width: double.infinity,
                            decoration: BoxDecoration(
                              color: const Color(0xFFF3F4F6),
                              borderRadius: BorderRadius.circular(6),
                            ),
                          ),
                          FractionallySizedBox(
                            widthFactor: value,
                            child: Container(
                              height: 12,
                              decoration: BoxDecoration(
                                gradient: LinearGradient(
                                  colors: [
                                    progressColor.withOpacity(0.7),
                                    progressColor,
                                  ],
                                ),
                                borderRadius: BorderRadius.circular(6),
                                boxShadow: [
                                  BoxShadow(
                                    color: progressColor.withOpacity(0.15),
                                    blurRadius: 6,
                                    offset: const Offset(0, 3),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ],
                      );
                    },
                  ),
                  const SizedBox(height: 24),

                  // Reorder Action Button
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: onReorder,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.primaryColor,
                        foregroundColor: Colors.white,
                        elevation: 0,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
                      ),
                      child: const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.replay_rounded, size: 18),
                          SizedBox(width: 8),
                          Text(
                            "Reorder Now",
                            style: TextStyle(
                              fontSize: 15,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
