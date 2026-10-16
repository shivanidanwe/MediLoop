import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';

class CustomBottomNavigation extends StatelessWidget {
  final int currentIndex;
  final ValueChanged<int> onTap;

  const CustomBottomNavigation({
    super.key,
    required this.currentIndex,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: const BorderRadius.only(
          topLeft: Radius.circular(28),
          topRight: Radius.circular(28),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 24,
            offset: const Offset(0, -6),
          ),
        ],
      ),
      child: SafeArea(
        top: false,
        child: Container(
          height: 88,
          padding: const EdgeInsets.symmetric(horizontal: 10),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildNavItem(
                index: 0,
                activeIcon: Icons.home_rounded,
                inactiveIcon: Icons.home_outlined,
                label: "Home",
              ),
              _buildNavItem(
                index: 1,
                activeIcon: Icons.notifications_rounded,
                inactiveIcon: Icons.notifications_outlined,
                label: "Notifications",
              ),
              _buildNavItem(
                index: 2,
                activeIcon: Icons.smart_toy_rounded,
                inactiveIcon: Icons.smart_toy_outlined,
                label: "AI Assistant",
                isSpecial: true,
              ),
              _buildNavItem(
                index: 3,
                activeIcon: Icons.shopping_cart_rounded,
                inactiveIcon: Icons.shopping_cart_outlined,
                label: "Cart",
              ),
              _buildNavItem(
                index: 4,
                activeIcon: Icons.person_rounded,
                inactiveIcon: Icons.person_outline_rounded,
                label: "Profile",
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildNavItem({
    required int index,
    required IconData activeIcon,
    required IconData inactiveIcon,
    required String label,
    bool isSpecial = false,
  }) {
    final bool isSelected = currentIndex == index;
    
    // Normal color logic
    final Color iconColor = isSpecial
        ? (isSelected ? Colors.white : AppTheme.textColorSecondary)
        : (isSelected ? AppTheme.primaryColor : AppTheme.textColorSecondary.withOpacity(0.7));
        
    final Color labelColor = isSelected ? AppTheme.primaryColor : AppTheme.textColorSecondary.withOpacity(0.8);

    return Expanded(
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: () => onTap(index),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            AnimatedContainer(
              duration: const Duration(milliseconds: 250),
              curve: Curves.easeInOut,
              padding: EdgeInsets.symmetric(
                horizontal: isSpecial ? 12 : 20,
                vertical: isSpecial ? 12 : 8,
              ),
              decoration: isSpecial
                  ? BoxDecoration(
                      shape: BoxShape.circle,
                      gradient: isSelected
                          ? const LinearGradient(
                              colors: [Color(0xFF164632), Color(0xFF2E7D5B)],
                              begin: Alignment.topLeft,
                              end: Alignment.bottomRight,
                            )
                          : LinearGradient(
                              colors: [Colors.grey.shade100, Colors.grey.shade200],
                            ),
                      boxShadow: isSelected
                          ? [
                              BoxShadow(
                                color: AppTheme.primaryColor.withOpacity(0.3),
                                blurRadius: 10,
                                offset: const Offset(0, 4),
                              ),
                            ]
                          : [],
                    )
                  : BoxDecoration(
                      color: isSelected
                          ? AppTheme.secondaryColor.withOpacity(0.7) // Mint style
                          : Colors.transparent,
                      borderRadius: BorderRadius.circular(16),
                    ),
              child: AnimatedScale(
                scale: isSelected ? 1.12 : 1.0,
                duration: const Duration(milliseconds: 200),
                child: Icon(
                  isSelected ? activeIcon : inactiveIcon,
                  color: iconColor,
                  size: isSpecial ? 24 : 22,
                ),
              ),
            ),
            const SizedBox(height: 6),
            Text(
              label,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                color: labelColor,
                fontSize: 10,
                fontWeight: isSelected ? FontWeight.w700 : FontWeight.w600,
                letterSpacing: -0.1,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
