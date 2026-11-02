import 'package:flutter/material.dart';
import '../../core/constants/app_strings.dart';
import '../../core/theme/app_theme.dart';
import '../../widgets/custom_text_field.dart';
import '../../widgets/liquid_glass_card.dart';
import '../../services/auth_service.dart';
import '../../services/profile_service.dart';
import '../../routes/app_routes.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();

  // Controllers
  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _ageController = TextEditingController();
  final _dobController = TextEditingController();
  DateTime? _selectedDob;

  final _addressController = TextEditingController();
  final _cityController = TextEditingController();
  final _stateController = TextEditingController();
  final _pincodeController = TextEditingController();
  final _allergiesController = TextEditingController();
  final _emergencyPhoneController = TextEditingController();

  bool _agreeToPrivacy = false;
  String? _selectedGender;
  String? _selectedRelationship;
  bool _isLoading = false;
  final _authService = AuthService();

  final List<String> _medicalConditions = [
    'Diabetes', 'Hypertension', 'Asthma', 'Heart Disease', 'Thyroid', 'None'
  ];
  final List<String> _selectedConditions = [];

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    _ageController.dispose();
    _dobController.dispose();
    _addressController.dispose();
    _cityController.dispose();
    _stateController.dispose();
    _pincodeController.dispose();
    _allergiesController.dispose();
    _emergencyPhoneController.dispose();
    super.dispose();
  }

  Future<void> _selectDob(BuildContext context) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: _selectedDob ?? DateTime(2000, 1, 1),
      firstDate: DateTime(1920),
      lastDate: DateTime.now(),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.light(
              primary: AppTheme.royalBlue,
            ),
          ),
          child: child!,
        );
      },
    );

    if (picked != null) {
      final now = DateTime.now();
      int calculatedAge = now.year - picked.year;
      if (now.month < picked.month || (now.month == picked.month && now.day < picked.day)) {
        calculatedAge--;
      }

      setState(() {
        _selectedDob = picked;
        _dobController.text =
            "${picked.day.toString().padLeft(2, '0')}/${picked.month.toString().padLeft(2, '0')}/${picked.year}";
        _ageController.text = "$calculatedAge";
      });
    }
  }

  void _showPrivacyPolicyDialog() {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          backgroundColor: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
          title: const Row(
            children: [
              Icon(Icons.privacy_tip_outlined, color: AppTheme.royalBlue),
              SizedBox(width: 10),
              Text(
                "MediLoop Privacy Policy",
                style: TextStyle(fontWeight: FontWeight.w800, fontSize: 18, color: AppTheme.midnightNavy),
              ),
            ],
          ),
          content: const SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  "Effective Date: August 2026\n\n"
                  "1. Data Privacy & Confidentiality\n"
                  "MediLoop protects your personal and health information using HIPAA-grade encryption and security headers.\n\n"
                  "2. Use of Medical Data\n"
                  "Your uploaded prescriptions, medical history, and allergy data are processed solely by our autonomous pharmacy AI agents to check drug interactions and ensure dosage safety.\n\n"
                  "3. Emergency Contact Sharing\n"
                  "Emergency contact numbers provided are strictly used for order safety verification and urgent clinical notifications.\n\n"
                  "4. Data Protection Rights\n"
                  "You maintain full ownership of your health records and can request profile updates or account deletion at any time.",
                  style: TextStyle(fontSize: 13, height: 1.5, color: AppTheme.textColorSecondary),
                ),
              ],
            ),
          ),
          actions: [
            ElevatedButton(
              onPressed: () {
                setState(() => _agreeToPrivacy = true);
                Navigator.pop(context);
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.royalBlue,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
              ),
              child: const Text("I Agree & Accept"),
            ),
          ],
        );
      },
    );
  }

  Future<void> _register() async {
    if (!_formKey.currentState!.validate() || !_agreeToPrivacy) return;

    if (_passwordController.text != _confirmPasswordController.text) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Passwords do not match'),
          backgroundColor: AppTheme.coral,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      );
      return;
    }

    setState(() => _isLoading = true);

    final result = await _authService.register(
      name: _nameController.text.trim(),
      email: _emailController.text.trim(),
      password: _passwordController.text,
      phoneNumber: _phoneController.text.trim(),
      age: int.tryParse(_ageController.text) ?? 25,
      gender: _selectedGender ?? 'Other',
      address: _addressController.text.trim(),
      city: _cityController.text.trim(),
      state: _stateController.text.trim(),
      pincode: _pincodeController.text.trim(),
      medicalConditions: _selectedConditions,
      allergies: _allergiesController.text.trim(),
      emergencyRelationship: _selectedRelationship ?? 'Other',
      emergencyPhone: _emergencyPhoneController.text.trim(),
    );

    if (!mounted) return;

    if (result['success'] == true) {
      final loginRes = await _authService.login(
        _emailController.text.trim(),
        _passwordController.text,
      );

      if (!mounted) return;
      setState(() => _isLoading = false);

      if (loginRes['user'] != null) {
        ProfileService().updateUser(loginRes['user']);
      }

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Registration Successful! Welcome to MediLoop.'),
          backgroundColor: AppTheme.mint.withOpacity(0.9),
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      );

      Navigator.pushNamedAndRemoveUntil(context, AppRoutes.home, (route) => false);
    } else {
      setState(() => _isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(result['message'] ?? 'Registration failed'),
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
          AppStrings.register,
          style: TextStyle(fontWeight: FontWeight.w800, fontSize: 18, color: AppTheme.midnightNavy),
        ),
        elevation: 0,
        backgroundColor: Colors.transparent,
        foregroundColor: AppTheme.midnightNavy,
      ),
      body: SingleChildScrollView(
        physics: const BouncingScrollPhysics(),
        padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 8.0),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              _buildSectionCard(
                title: "Personal Credentials",
                icon: Icons.badge_outlined,
                children: [
                  CustomTextField(
                    controller: _nameController,
                    labelText: AppStrings.fullName,
                    hintText: "Shivani More",
                    prefixIcon: Icons.person_outline_rounded,
                    validator: (v) => v!.isEmpty ? "Required" : null,
                  ),
                  CustomTextField(
                    controller: _phoneController,
                    labelText: AppStrings.mobileNumber,
                    hintText: "10-digit mobile number",
                    prefixIcon: Icons.phone_android_rounded,
                    keyboardType: TextInputType.phone,
                    validator: (v) => (v == null || v.length != 10) ? "Enter valid 10 digits" : null,
                  ),
                  CustomTextField(
                    controller: _emailController,
                    labelText: AppStrings.email,
                    hintText: "name@example.com",
                    prefixIcon: Icons.alternate_email_rounded,
                    keyboardType: TextInputType.emailAddress,
                    validator: (v) => (v == null || !v.contains('@')) ? "Invalid email" : null,
                  ),
                  CustomTextField(
                    controller: _passwordController,
                    labelText: AppStrings.password,
                    hintText: "Min. 6 characters",
                    prefixIcon: Icons.lock_outline_rounded,
                    obscureText: true,
                    validator: (v) => (v == null || v.length < 6) ? "Min 6 chars" : null,
                  ),
                  CustomTextField(
                    controller: _confirmPasswordController,
                    labelText: AppStrings.confirmPassword,
                    hintText: "Re-enter password",
                    prefixIcon: Icons.lock_reset_rounded,
                    obscureText: true,
                    validator: (v) => v != _passwordController.text ? "Passwords don't match" : null,
                  ),
                ],
              ),
              const SizedBox(height: 16),

              _buildSectionCard(
                title: "Demographics",
                icon: Icons.calendar_today_outlined,
                children: [
                  GestureDetector(
                    onTap: () => _selectDob(context),
                    child: AbsorbPointer(
                      child: CustomTextField(
                        controller: _dobController,
                        labelText: "Date of Birth (DD/MM/YYYY)",
                        hintText: "Tap to select your date of birth",
                        prefixIcon: Icons.calendar_month_rounded,
                        suffixIcon: const Icon(Icons.arrow_drop_down, color: AppTheme.royalBlue),
                        validator: (v) => v == null || v.isEmpty ? "Please select Date of Birth" : null,
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                  CustomTextField(
                    controller: _ageController,
                    labelText: "Calculated Age",
                    hintText: "Computed automatically from DOB",
                    prefixIcon: Icons.cake_outlined,
                    keyboardType: TextInputType.number,
                    enabled: false,
                    validator: (v) => v == null || v.isEmpty ? "Age required" : null,
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    decoration: InputDecoration(
                      labelText: AppStrings.gender,
                      prefixIcon: const Icon(Icons.people_outline_rounded, color: AppTheme.royalBlue),
                      filled: true,
                      fillColor: Colors.white.withOpacity(0.9),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 15),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(16),
                        borderSide: BorderSide(color: Colors.grey.shade200, width: 1.2),
                      ),
                    ),
                    items: ['Male', 'Female', 'Other'].map((String value) {
                      return DropdownMenuItem<String>(
                        value: value,
                        child: Text(value, style: const TextStyle(fontWeight: FontWeight.w600)),
                      );
                    }).toList(),
                    onChanged: (v) => setState(() => _selectedGender = v),
                    validator: (v) => v == null ? "Select gender" : null,
                  ),
                ],
              ),
              const SizedBox(height: 16),

              _buildSectionCard(
                title: "Delivery Address",
                icon: Icons.local_shipping_outlined,
                children: [
                  CustomTextField(
                    controller: _addressController,
                    labelText: AppStrings.address,
                    hintText: "Apartment / House / Street",
                    prefixIcon: Icons.home_outlined,
                    maxLines: 2,
                    validator: (v) => v!.isEmpty ? "Required" : null,
                  ),
                  CustomTextField(
                    controller: _cityController,
                    labelText: AppStrings.city,
                    hintText: "Pandharpur",
                    prefixIcon: Icons.location_city_rounded,
                    validator: (v) => v!.isEmpty ? "Required" : null,
                  ),
                  CustomTextField(
                    controller: _stateController,
                    labelText: AppStrings.state,
                    hintText: "Maharashtra",
                    prefixIcon: Icons.map_outlined,
                    validator: (v) => v!.isEmpty ? "Required" : null,
                  ),
                  CustomTextField(
                    controller: _pincodeController,
                    labelText: AppStrings.pincode,
                    hintText: "413304",
                    prefixIcon: Icons.pin_drop_outlined,
                    keyboardType: TextInputType.number,
                    validator: (v) => (v == null || v.length != 6) ? "Enter valid 6 digits" : null,
                  ),
                ],
              ),
              const SizedBox(height: 16),

              _buildSectionCard(
                title: "Medical Profile",
                icon: Icons.healing_outlined,
                children: [
                  const Text(
                    "Known Conditions",
                    style: TextStyle(fontWeight: FontWeight.w700, fontSize: 13, color: AppTheme.midnightNavy),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8.0,
                    runSpacing: 6.0,
                    children: _medicalConditions.map((condition) {
                      final isSelected = _selectedConditions.contains(condition);
                      return FilterChip(
                        label: Text(condition),
                        selected: isSelected,
                        labelStyle: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w700,
                          color: isSelected ? AppTheme.royalBlue : AppTheme.textColorSecondary,
                        ),
                        backgroundColor: Colors.white,
                        selectedColor: AppTheme.royalBlue.withOpacity(0.12),
                        checkmarkColor: AppTheme.royalBlue,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                          side: BorderSide(
                            color: isSelected ? AppTheme.royalBlue : Colors.grey.shade300,
                            width: 1.2,
                          ),
                        ),
                        onSelected: (selected) {
                          setState(() {
                            if (selected) {
                              _selectedConditions.add(condition);
                            } else {
                              _selectedConditions.remove(condition);
                            }
                          });
                        },
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 12),
                  CustomTextField(
                    controller: _allergiesController,
                    labelText: AppStrings.allergies,
                    hintText: "Penicillin, Sulfa drugs, etc.",
                    prefixIcon: Icons.warning_amber_rounded,
                    maxLines: 2,
                  ),
                ],
              ),
              const SizedBox(height: 16),

              _buildSectionCard(
                title: "Emergency Contact",
                icon: Icons.contact_emergency_outlined,
                children: [
                  DropdownButtonFormField<String>(
                    decoration: InputDecoration(
                      labelText: AppStrings.relationship,
                      prefixIcon: const Icon(Icons.family_restroom_rounded, color: AppTheme.royalBlue),
                      filled: true,
                      fillColor: Colors.white.withOpacity(0.9),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 15),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(16),
                        borderSide: BorderSide(color: Colors.grey.shade200, width: 1.2),
                      ),
                    ),
                    items: ['Mother', 'Father', 'Brother', 'Sister', 'Spouse', 'Friend', 'Other']
                        .map((String value) {
                      return DropdownMenuItem<String>(
                        value: value,
                        child: Text(value, style: const TextStyle(fontWeight: FontWeight.w600)),
                      );
                    }).toList(),
                    onChanged: (v) => setState(() => _selectedRelationship = v),
                    validator: (v) => v == null ? "Select relationship" : null,
                  ),
                  const SizedBox(height: 12),
                  CustomTextField(
                    controller: _emergencyPhoneController,
                    labelText: "Emergency Phone",
                    hintText: "10-digit emergency number",
                    prefixIcon: Icons.phone_forwarded_rounded,
                    keyboardType: TextInputType.phone,
                    validator: (v) => (v == null || v.length != 10) ? "Enter 10 digits" : null,
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Privacy Acceptance Checkbox
              LiquidGlassCard(
                borderRadius: 18,
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                child: CheckboxListTile(
                  value: _agreeToPrivacy,
                  onChanged: (v) => setState(() => _agreeToPrivacy = v ?? false),
                  title: Row(
                    children: [
                      const Text(
                        "I agree to ",
                        style: TextStyle(fontSize: 13, fontWeight: FontWeight.w500, color: AppTheme.midnightNavy),
                      ),
                      GestureDetector(
                        onTap: _showPrivacyPolicyDialog,
                        child: const Text(
                          "Privacy Policy",
                          style: TextStyle(
                            color: AppTheme.royalBlue,
                            fontWeight: FontWeight.w700,
                            fontSize: 13,
                            decoration: TextDecoration.underline,
                          ),
                        ),
                      ),
                    ],
                  ),
                  controlAffinity: ListTileControlAffinity.leading,
                  activeColor: AppTheme.royalBlue,
                ),
              ),
              const SizedBox(height: 24),

              // Register Action Button
              Container(
                height: 52,
                width: double.infinity,
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
                      blurRadius: 18,
                      offset: const Offset(0, 6),
                    ),
                  ],
                ),
                child: ElevatedButton(
                  onPressed: (_agreeToPrivacy && !_isLoading) ? _register : null,
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
                      : const Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(
                              AppStrings.register,
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w700,
                                color: Colors.white,
                                letterSpacing: 0.2,
                              ),
                            ),
                            SizedBox(width: 8),
                            Icon(Icons.check_circle_outline_rounded, size: 20, color: Colors.white),
                          ],
                        ),
                ),
              ),
              const SizedBox(height: 36),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSectionCard({
    required String title,
    required IconData icon,
    required List<Widget> children,
  }) {
    return LiquidGlassCard(
      borderRadius: 22,
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppTheme.royalBlue.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(icon, size: 20, color: AppTheme.royalBlue),
              ),
              const SizedBox(width: 12),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w800,
                  color: AppTheme.midnightNavy,
                  letterSpacing: -0.3,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Divider(height: 1, color: Color(0x2064748B)),
          const SizedBox(height: 12),
          ...children,
        ],
      ),
    );
  }
}
