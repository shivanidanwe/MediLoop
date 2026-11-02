import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import '../models/user_model.dart';
import '../routes/app_routes.dart';

class CustomHomeAppBar extends StatelessWidget {
  final UserModel user;

  const CustomHomeAppBar({super.key, required this.user});

  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) {
      return "Good morning";
    } else if (hour < 17) {
      return "Good afternoon";
    } else {
      return "Good evening";
    }
  }

  @override
  Widget build(BuildContext context) {
    final cleanWords = user.name.trim().split(RegExp(r'\s+')).where((n) => n.isNotEmpty).toList();
    final String initials = cleanWords.isNotEmpty
        ? cleanWords.map((n) => n[0]).take(2).join().toUpperCase()
        : "PT";

    return Container(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 12),
      color: Colors.transparent,
      child: Row(
        children: [
          // User Avatar with gradient border
          Container(
            padding: const EdgeInsets.all(2.5),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [AppTheme.royalBlue, AppTheme.electricCyan],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: AppTheme.royalBlue.withOpacity(0.25),
                  blurRadius: 12,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: CircleAvatar(
              radius: 21,
              backgroundColor: Colors.white,
              child: Text(
                initials,
                style: const TextStyle(
                  color: AppTheme.royalBlue,
                  fontWeight: FontWeight.w800,
                  fontSize: 15,
                ),
              ),
            ),
          ),
          const SizedBox(width: 14),

          // Greeting & Patient Name
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      "${_getGreeting()} 👋",
                      style: TextStyle(
                        fontSize: 12,
                        color: AppTheme.textColorSecondary.withOpacity(0.9),
                        fontWeight: FontWeight.w600,
                        letterSpacing: 0.2,
                      ),
                    ),
                    const SizedBox(width: 6),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: AppTheme.mint.withOpacity(0.5),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: const Text(
                        "ONLINE",
                        style: TextStyle(
                          fontSize: 9,
                          fontWeight: FontWeight.w800,
                          color: Color(0xFF047857),
                          letterSpacing: 0.5,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 2),
                Text(
                  user.name.isEmpty ? "Patient" : user.name,
                  style: const TextStyle(
                    fontWeight: FontWeight.w800,
                    color: AppTheme.midnightNavy,
                    fontSize: 19,
                    letterSpacing: -0.5,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
          const SizedBox(width: 12),

          // Notification Bell with Glass Glow
          GestureDetector(
            onTap: () => Navigator.pushNamed(context, AppRoutes.notifications),
            child: Container(
              width: 44,
              height: 44,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: Colors.grey.shade200,
                  width: 1.2,
                ),
                boxShadow: [
                  BoxShadow(
                    color: AppTheme.midnightNavy.withOpacity(0.04),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Stack(
                alignment: Alignment.center,
                children: [
                  const Icon(
                    Icons.notifications_outlined,
                    color: AppTheme.midnightNavy,
                    size: 22,
                  ),
                  Positioned(
                    top: 10,
                    right: 11,
                    child: Container(
                      width: 8,
                      height: 8,
                      decoration: BoxDecoration(
                        color: AppTheme.coral,
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white, width: 1.5),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
