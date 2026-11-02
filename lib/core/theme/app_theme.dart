import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Next-Generation Liquid Glass Design System for MediLoop
/// Inspired by Apple Liquid Glass, modern SaaS, and futuristic healthcare technology.
class AppTheme {
  // --- PRIMARY PALETTE ---
  static const Color midnightNavy = Color(0xFF07152F);
  static const Color deepBlue = Color(0xFF102A56);
  static const Color electricCyan = Color(0xFF27D8E8);
  static const Color aqua = Color(0xFF49E5D1);
  static const Color royalBlue = Color(0xFF477BFF);
  static const Color violet = Color(0xFF8865F7);
  static const Color lavender = Color(0xFFB99CFF);

  // --- SUPPORTING PALETTE ---
  static const Color softPink = Color(0xFFFF8FCB);
  static const Color coral = Color(0xFFFF8C83);
  static const Color warmYellow = Color(0xFFFFD477);
  static const Color mint = Color(0xFFB8F5DE);
  static const Color cloudWhite = Color(0xFFF7F9FF);
  static const Color glassWhite = Color(0xB8FFFFFF); // rgba(255, 255, 255, 0.72)
  static const Color glassCardBg = Color(0xCCFFFFFF); // 80% opacity white
  static const Color glassBorder = Color(0x40FFFFFF); // 25% luminous white
  static const Color darkGlassBg = Color(0xCC07152F); // 80% midnight navy

  // --- FUNCTIONAL ALIASES (Backward Compatible) ---
  static const Color primaryColor = royalBlue;
  static const Color secondaryColor = mint;
  static const Color accentColor = electricCyan;
  static const Color backgroundColor = cloudWhite;
  static const Color cardColor = Colors.white;
  static const Color textColorPrimary = midnightNavy;
  static const Color textColorSecondary = Color(0xFF64748B); // Slate 500

  // --- GRADIENTS ---
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [royalBlue, electricCyan],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient heroGradient = LinearGradient(
    colors: [midnightNavy, deepBlue, royalBlue],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient aiGradient = LinearGradient(
    colors: [electricCyan, royalBlue, violet],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient accentCyanGradient = LinearGradient(
    colors: [electricCyan, aqua],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient violetGradient = LinearGradient(
    colors: [violet, lavender],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient sunsetGradient = LinearGradient(
    colors: [softPink, warmYellow],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient glassCardGradient = LinearGradient(
    colors: [
      Color(0xE6FFFFFF),
      Color(0xB3FFFFFF),
    ],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  // --- LIQUID GLASS DECORATIONS ---
  static BoxDecoration glassCardDecoration({
    double radius = 22,
    Color? borderColor,
    List<BoxShadow>? shadows,
  }) {
    return BoxDecoration(
      color: glassCardBg,
      borderRadius: BorderRadius.circular(radius),
      border: Border.all(
        color: borderColor ?? const Color(0x66E2E8F0),
        width: 1.2,
      ),
      boxShadow: shadows ??
          [
            BoxShadow(
              color: midnightNavy.withOpacity(0.04),
              blurRadius: 20,
              offset: const Offset(0, 8),
            ),
            BoxShadow(
              color: royalBlue.withOpacity(0.02),
              blurRadius: 10,
              offset: const Offset(0, 2),
            ),
          ],
    );
  }

  static BoxDecoration luminousGlassDecoration({
    double radius = 24,
    Gradient? gradient,
  }) {
    return BoxDecoration(
      gradient: gradient ??
          LinearGradient(
            colors: [
              Colors.white.withOpacity(0.85),
              Colors.white.withOpacity(0.65),
            ],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
      borderRadius: BorderRadius.circular(radius),
      border: Border.all(
        color: Colors.white.withOpacity(0.8),
        width: 1.5,
      ),
      boxShadow: [
        BoxShadow(
          color: midnightNavy.withOpacity(0.06),
          blurRadius: 24,
          offset: const Offset(0, 10),
        ),
      ],
    );
  }

  // --- MATERIAL 3 THEME ---
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      scaffoldBackgroundColor: cloudWhite,
      colorScheme: ColorScheme.fromSeed(
        seedColor: royalBlue,
        primary: royalBlue,
        secondary: electricCyan,
        surface: Colors.white,
        onPrimary: Colors.white,
        onSecondary: midnightNavy,
      ),
      cardTheme: CardThemeData(
        color: Colors.white,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(22),
          side: const BorderSide(color: Color(0x33E2E8F0), width: 1.2),
        ),
        margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: royalBlue,
          foregroundColor: Colors.white,
          minimumSize: const Size(double.infinity, 52),
          elevation: 0,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          textStyle: GoogleFonts.plusJakartaSans(
            fontSize: 15,
            fontWeight: FontWeight.w700,
            letterSpacing: -0.2,
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white.withOpacity(0.85),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(18),
          borderSide: const BorderSide(color: Color(0x4DE2E8F0), width: 1.2),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(18),
          borderSide: const BorderSide(color: Color(0x4DE2E8F0), width: 1.2),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(18),
          borderSide: const BorderSide(color: royalBlue, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(18),
          borderSide: const BorderSide(color: coral, width: 1.2),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        prefixIconColor: royalBlue,
        hintStyle: GoogleFonts.plusJakartaSans(
          color: textColorSecondary.withOpacity(0.7),
          fontSize: 14,
        ),
      ),
      textTheme: GoogleFonts.plusJakartaSansTextTheme().copyWith(
        headlineLarge: GoogleFonts.plusJakartaSans(
          fontSize: 32,
          fontWeight: FontWeight.w800,
          color: midnightNavy,
          letterSpacing: -0.8,
        ),
        headlineMedium: GoogleFonts.plusJakartaSans(
          fontSize: 24,
          fontWeight: FontWeight.w800,
          color: midnightNavy,
          letterSpacing: -0.5,
        ),
        titleLarge: GoogleFonts.plusJakartaSans(
          fontSize: 20,
          fontWeight: FontWeight.w700,
          color: midnightNavy,
          letterSpacing: -0.3,
        ),
        titleMedium: GoogleFonts.plusJakartaSans(
          fontSize: 16,
          fontWeight: FontWeight.w700,
          color: midnightNavy,
        ),
        bodyLarge: GoogleFonts.plusJakartaSans(
          fontSize: 15,
          color: midnightNavy,
          fontWeight: FontWeight.w500,
        ),
        bodyMedium: GoogleFonts.plusJakartaSans(
          fontSize: 14,
          color: textColorSecondary,
          fontWeight: FontWeight.w400,
        ),
      ),
    );
  }
}
