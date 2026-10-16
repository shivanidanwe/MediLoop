import 'package:flutter/material.dart';
import '../screens/splash/splash_screen.dart';
import '../screens/login/login_screen.dart';
import '../screens/register/register_screen.dart';
import '../screens/forgot_password/forgot_password_screen.dart';
import '../screens/home/home_screen.dart';
import '../screens/ai_chat/ai_chat_screen.dart';
import '../screens/search_medicines/search_medicines_screen.dart';
import '../screens/medicine_details/medicine_details_screen.dart';
import '../screens/cart/cart_screen.dart';
import '../screens/payment/payment_screen.dart';
import '../screens/upload_prescription/upload_prescription_screen.dart';
import '../screens/order_success/order_success_screen.dart';
import '../screens/order_tracking/order_tracking_screen.dart';
import '../screens/notifications/notifications_screen.dart';
import '../screens/settings/settings_screen.dart';
import '../screens/about_app/about_app_screen.dart';

class AppRoutes {
  static const String splash = '/';
  static const String login = '/login';
  static const String register = '/register';
  static const String forgotPassword = '/forgot-password';
  static const String home = '/home';
  static const String aiChat = '/ai-chat';
  
  // New Flow screens
  static const String searchMedicines = '/search-medicines';
  static const String medicineDetails = '/medicine-details';
  static const String cart = '/cart';
  static const String payment = '/payment';
  static const String uploadPrescription = '/upload-prescription';
  static const String orderSuccess = '/order-success';
  static const String orderTracking = '/order-tracking';
  static const String notifications = '/notifications';
  static const String settings = '/settings';
  static const String aboutApp = '/about-app';

  static Map<String, WidgetBuilder> get routes => {
        splash: (context) => const SplashScreen(),
        login: (context) => const LoginScreen(),
        register: (context) => const RegisterScreen(),
        forgotPassword: (context) => const ForgotPasswordScreen(),
        home: (context) => const HomeScreen(),
        aiChat: (context) => const AIChatScreen(),
        
        // New routes mapping
        searchMedicines: (context) => const SearchMedicinesScreen(),
        medicineDetails: (context) => const MedicineDetailsScreen(),
        cart: (context) => const CartScreen(),
        payment: (context) => const PaymentScreen(),
        uploadPrescription: (context) => const UploadPrescriptionScreen(),
        orderSuccess: (context) => const OrderSuccessScreen(),
        orderTracking: (context) => const OrderTrackingScreen(),
        notifications: (context) => const NotificationsScreen(),
        settings: (context) => const SettingsScreen(),
        aboutApp: (context) => const AboutAppScreen(),
      };
}
