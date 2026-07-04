import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';

class RefillCard extends StatelessWidget {
  final String medicineName;
  final int daysLeft;
  final VoidCallback onOrderAgain;
  final VoidCallback onRemindLater;

  const RefillCard({
    super.key,
    required this.medicineName,
    required this.daysLeft,
    required this.onOrderAgain,
    required this.onRemindLater,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Colors.orange.shade50,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: Colors.orange.shade200),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.history_outlined, color: Colors.orange),
                const SizedBox(width: 8),
                const Text(
                  "AI Refill Reminder",
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.orange,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              medicineName,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              "Estimated to finish in $daysLeft days.",
              style: TextStyle(color: Colors.grey.shade700),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    onPressed: onOrderAgain,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.orange,
                      minimumSize: const Size(0, 40),
                    ),
                    child: const Text("Order Again"),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton(
                    onPressed: onRemindLater,
                    style: OutlinedButton.styleFrom(
                      side: const BorderSide(color: Colors.orange),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                      minimumSize: const Size(0, 40),
                    ),
                    child: const Text(
                      "Remind Later",
                      style: TextStyle(color: Colors.orange),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
