import 'package:flutter/material.dart';
import '../screens/splash/splash_screen.dart';
import '../screens/login/login_screen.dart';
import '../screens/register/register_screen.dart';
import '../screens/forgot_password/forgot_password_screen.dart';
import '../screens/home/home_screen.dart';
import '../screens/ai_chat/ai_chat_screen.dart';

class AppRoutes {
  static const String splash = '/';
  static const String login = '/login';
  static const String register = '/register';
  static const String forgotPassword = '/forgot-password';
  static const String home = '/home';
  static const String aiChat = '/ai-chat';

  static Map<String, WidgetBuilder> get routes => {
        splash: (context) => const SplashScreen(),
        login: (context) => const LoginScreen(),
        register: (context) => const RegisterScreen(),
        forgotPassword: (context) => const ForgotPasswordScreen(),
        home: (context) => const HomeScreen(),
        aiChat: (context) => const AIChatScreen(),
      };
}
