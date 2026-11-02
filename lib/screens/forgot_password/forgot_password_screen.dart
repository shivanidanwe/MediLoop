import 'package:flutter/material.dart';
import '../../core/constants/app_strings.dart';
import '../../core/theme/app_theme.dart';
import '../../widgets/custom_text_field.dart';
import '../../widgets/liquid_glass_card.dart';
import '../../services/auth_service.dart';

class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  int _currentStep = 0; // 0: Email, 1: OTP, 2: New Password
  final _emailFormKey = GlobalKey<FormState>();
  final _otpFormKey = GlobalKey<FormState>();
  final _passwordFormKey = GlobalKey<FormState>();

  final _emailController = TextEditingController();
  final _otpController = TextEditingController();
  final _newPasswordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  bool _obscurePassword = true;
  bool _isLoading = false;
  final AuthService _authService = AuthService();

  @override
  void dispose() {
    _emailController.dispose();
    _otpController.dispose();
    _newPasswordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> _sendOtp() async {
    if (!_emailFormKey.currentState!.validate()) return;

    setState(() => _isLoading = true);
    final result = await _authService.forgotPassword(_emailController.text.trim());

    if (!mounted) return;
    setState(() => _isLoading = false);

    if (result['success'] == true) {
      final msg = result['message'] ?? 'OTP code sent to email!';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(msg),
          duration: const Duration(seconds: 5),
          backgroundColor: AppTheme.royalBlue,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      );
      setState(() => _currentStep = 1);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(result['message'] ?? 'Failed to send OTP'),
          backgroundColor: AppTheme.coral,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      );
    }
  }

  Future<void> _verifyOtp() async {
    if (!_otpFormKey.currentState!.validate()) return;

    setState(() => _isLoading = true);
    final result = await _authService.verifyOtp(_emailController.text.trim(), _otpController.text.trim());

    if (!mounted) return;
    setState(() => _isLoading = false);

    if (result['success'] == true) {
      setState(() => _currentStep = 2);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(result['message'] ?? 'Invalid OTP code.'),
          backgroundColor: AppTheme.coral,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      );
    }
  }

  Future<void> _resetPassword() async {
    if (!_passwordFormKey.currentState!.validate()) return;

    setState(() => _isLoading = true);
    final result = await _authService.resetPassword(
      _emailController.text.trim(),
      _otpController.text.trim(),
      _newPasswordController.text,
    );

    if (!mounted) return;
    setState(() => _isLoading = false);

    if (result['success'] == true) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Password reset successfully! Please login with your new password.'),
          backgroundColor: AppTheme.mint.withOpacity(0.9),
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      );
      Navigator.pop(context);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(result['message'] ?? 'Password reset failed'),
          backgroundColor: AppTheme.coral,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.cloudWhite,
      appBar: AppBar(
        title: const Text(
          "Password Recovery",
          style: TextStyle(fontWeight: FontWeight.w800, fontSize: 18, color: AppTheme.midnightNavy),
        ),
        elevation: 0,
        backgroundColor: Colors.transparent,
        foregroundColor: AppTheme.midnightNavy,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Step Indicators
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  _buildStepDot(0, "Email"),
                  _buildStepLine(0),
                  _buildStepDot(1, "OTP Code"),
                  _buildStepLine(1),
                  _buildStepDot(2, "New Password"),
                ],
              ),
              const SizedBox(height: 32),

              if (_currentStep == 0) _buildEmailStep(),
              if (_currentStep == 1) _buildOtpStep(),
              if (_currentStep == 2) _buildNewPasswordStep(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStepDot(int step, String label) {
    final bool isActive = _currentStep == step;
    final bool isDone = _currentStep > step;

    return Column(
      children: [
        Container(
          width: 32,
          height: 32,
          decoration: BoxDecoration(
            color: isDone
                ? AppTheme.mint
                : (isActive ? AppTheme.royalBlue : Colors.grey.shade200),
            shape: BoxShape.circle,
            boxShadow: isActive
                ? [
                    BoxShadow(
                      color: AppTheme.royalBlue.withOpacity(0.3),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    )
                  ]
                : [],
          ),
          child: Center(
            child: isDone
                ? const Icon(Icons.check, size: 16, color: AppTheme.midnightNavy)
                : Text(
                    "${step + 1}",
                    style: TextStyle(
                      color: isActive ? Colors.white : AppTheme.textColorSecondary,
                      fontWeight: FontWeight.w700,
                      fontSize: 12,
                    ),
                  ),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 10,
            fontWeight: isActive ? FontWeight.w700 : FontWeight.w500,
            color: isActive ? AppTheme.royalBlue : AppTheme.textColorSecondary,
          ),
        ),
      ],
    );
  }

  Widget _buildStepLine(int afterStep) {
    final bool isPassed = _currentStep > afterStep;
    return Container(
      width: 40,
      height: 2,
      margin: const EdgeInsets.only(bottom: 16, left: 4, right: 4),
      color: isPassed ? AppTheme.royalBlue : Colors.grey.shade300,
    );
  }

  Widget _buildEmailStep() {
    return Form(
      key: _emailFormKey,
      child: LiquidGlassCard(
        borderRadius: 24,
        padding: const EdgeInsets.all(24),
        hasGlow: true,
        glowColor: AppTheme.royalBlue,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Icon(Icons.mark_email_read_outlined, size: 48, color: AppTheme.royalBlue),
            const SizedBox(height: 16),
            const Text(
              "Reset via Registered Email",
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: AppTheme.midnightNavy),
            ),
            const SizedBox(height: 8),
            Text(
              "Enter your MediLoop registered email address. We will transmit a secure 6-digit verification code.",
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 13, color: AppTheme.textColorSecondary.withOpacity(0.9), height: 1.4),
            ),
            const SizedBox(height: 24),
            CustomTextField(
              controller: _emailController,
              labelText: AppStrings.email,
              hintText: "patient@mediloop.com",
              prefixIcon: Icons.alternate_email_rounded,
              keyboardType: TextInputType.emailAddress,
              validator: (v) => (v == null || !v.contains('@')) ? "Please enter valid email" : null,
            ),
            const SizedBox(height: 24),
            _buildActionButton("Send Security Code", _sendOtp),
          ],
        ),
      ),
    );
  }

  Widget _buildOtpStep() {
    return Form(
      key: _otpFormKey,
      child: LiquidGlassCard(
        borderRadius: 24,
        padding: const EdgeInsets.all(24),
        hasGlow: true,
        glowColor: AppTheme.electricCyan,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Icon(Icons.security_rounded, size: 48, color: AppTheme.electricCyan),
            const SizedBox(height: 16),
            const Text(
              "Enter 6-Digit Code",
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: AppTheme.midnightNavy),
            ),
            const SizedBox(height: 8),
            Text(
              "Enter the verification code dispatched to ${_emailController.text}",
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 13, color: AppTheme.textColorSecondary.withOpacity(0.9), height: 1.4),
            ),
            const SizedBox(height: 24),
            CustomTextField(
              controller: _otpController,
              labelText: "Security OTP Code",
              hintText: "123456",
              prefixIcon: Icons.pin_outlined,
              keyboardType: TextInputType.number,
              validator: (v) => (v == null || v.length < 4) ? "Enter valid OTP code" : null,
            ),
            const SizedBox(height: 24),
            _buildActionButton("Verify Security Code", _verifyOtp),
          ],
        ),
      ),
    );
  }

  Widget _buildNewPasswordStep() {
    return Form(
      key: _passwordFormKey,
      child: LiquidGlassCard(
        borderRadius: 24,
        padding: const EdgeInsets.all(24),
        hasGlow: true,
        glowColor: AppTheme.royalBlue,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Icon(Icons.lock_reset_rounded, size: 48, color: AppTheme.royalBlue),
            const SizedBox(height: 16),
            const Text(
              "Set New Password",
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: AppTheme.midnightNavy),
            ),
            const SizedBox(height: 8),
            Text(
              "Create a strong password with at least 6 characters for your patient account.",
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 13, color: AppTheme.textColorSecondary.withOpacity(0.9)),
            ),
            const SizedBox(height: 24),
            CustomTextField(
              controller: _newPasswordController,
              labelText: "New Password",
              hintText: "Min. 6 characters",
              prefixIcon: Icons.lock_outline_rounded,
              obscureText: _obscurePassword,
              suffixIcon: IconButton(
                icon: Icon(
                  _obscurePassword ? Icons.visibility_off_outlined : Icons.visibility_outlined,
                  color: AppTheme.royalBlue,
                  size: 20,
                ),
                onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
              ),
              validator: (v) => (v == null || v.length < 6) ? "Min. 6 characters required" : null,
            ),
            const SizedBox(height: 12),
            CustomTextField(
              controller: _confirmPasswordController,
              labelText: "Confirm New Password",
              hintText: "Re-enter new password",
              prefixIcon: Icons.lock_clock_outlined,
              obscureText: _obscurePassword,
              validator: (v) => v != _newPasswordController.text ? "Passwords do not match" : null,
            ),
            const SizedBox(height: 24),
            _buildActionButton("Save New Password", _resetPassword),
          ],
        ),
      ),
    );
  }

  Widget _buildActionButton(String label, VoidCallback onPressed) {
    return Container(
      height: 52,
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [AppTheme.royalBlue, Color(0xFF2563EB)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: AppTheme.royalBlue.withOpacity(0.3),
            blurRadius: 16,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: ElevatedButton(
        onPressed: _isLoading ? null : onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.transparent,
          shadowColor: Colors.transparent,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        ),
        child: _isLoading
            ? const SizedBox(
                height: 20,
                width: 20,
                child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
              )
            : Text(
                label,
                style: const TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                  color: Colors.white,
                ),
              ),
      ),
    );
  }
}
