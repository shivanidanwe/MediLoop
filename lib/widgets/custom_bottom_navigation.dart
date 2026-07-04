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
          topLeft: Radius.circular(24),
          topRight: Radius.circular(24),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.06),
            blurRadius: 20,
            offset: const Offset(0, -4),
          ),
        ],
      ),
      child: SafeArea(
        top: false,
        child: Container(
          height: 80,
          padding: const EdgeInsets.symmetric(horizontal: 8),
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
    final Color color = isSelected ? AppTheme.primaryColor : Colors.grey.shade500;

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
                horizontal: isSpecial ? 16 : 20,
                vertical: 8,
              ),
              decoration: BoxDecoration(
                color: isSelected
                    ? AppTheme.primaryColor.withOpacity(0.08)
                    : Colors.transparent,
                borderRadius: BorderRadius.circular(16),
              ),
              child: AnimatedScale(
                scale: isSelected ? 1.15 : 1.0,
                duration: const Duration(milliseconds: 200),
                child: Icon(
                  isSelected ? activeIcon : inactiveIcon,
                  color: color,
                  size: isSpecial ? 26 : 24,
                ),
              ),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                color: color,
                fontSize: 11,
                fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
