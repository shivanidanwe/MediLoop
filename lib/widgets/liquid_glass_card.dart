import 'dart:ui';
import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';

class LiquidGlassCard extends StatelessWidget {
  final Widget child;
  final double borderRadius;
  final EdgeInsetsGeometry padding;
  final EdgeInsetsGeometry? margin;
  final Gradient? gradient;
  final Color? backgroundColor;
  final Color? borderColor;
  final double borderWidth;
  final double blurSigma;
  final VoidCallback? onTap;
  final bool hasGlow;
  final Color? glowColor;

  const LiquidGlassCard({
    super.key,
    required this.child,
    this.borderRadius = 22,
    this.padding = const EdgeInsets.all(20),
    this.margin,
    this.gradient,
    this.backgroundColor,
    this.borderColor,
    this.borderWidth = 1.2,
    this.blurSigma = 12.0,
    this.onTap,
    this.hasGlow = false,
    this.glowColor,
  });

  @override
  Widget build(BuildContext context) {
    Widget content = Container(
      margin: margin,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(borderRadius),
        boxShadow: [
          if (hasGlow)
            BoxShadow(
              color: (glowColor ?? AppTheme.royalBlue).withOpacity(0.18),
              blurRadius: 28,
              offset: const Offset(0, 10),
            )
          else
            BoxShadow(
              color: AppTheme.midnightNavy.withOpacity(0.04),
              blurRadius: 20,
              offset: const Offset(0, 8),
            ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(borderRadius),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: blurSigma, sigmaY: blurSigma),
          child: Container(
            padding: padding,
            decoration: BoxDecoration(
              gradient: gradient ??
                  LinearGradient(
                    colors: [
                      (backgroundColor ?? Colors.white).withOpacity(0.85),
                      (backgroundColor ?? Colors.white).withOpacity(0.65),
                    ],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
              borderRadius: BorderRadius.circular(borderRadius),
              border: Border.all(
                color: borderColor ?? Colors.white.withOpacity(0.65),
                width: borderWidth,
              ),
            ),
            child: child,
          ),
        ),
      ),
    );

    if (onTap != null) {
      return GestureDetector(
        onTap: onTap,
        behavior: HitTestBehavior.opaque,
        child: content,
      );
    }

    return content;
  }
}

