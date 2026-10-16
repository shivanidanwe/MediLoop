import 'package:flutter/material.dart';
import '../../core/constants/app_strings.dart';
import '../../core/theme/app_theme.dart';
import '../../widgets/custom_text_field.dart';

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
              primary: AppTheme.primaryColor,
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
        _dobController.text = "${picked.day.toString().padLeft(2, '0')}/${picked.month.toString().padLeft(2, '0')}/${picked.year}";
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
              Icon(Icons.privacy_tip_outlined, color: AppTheme.primaryColor),
              SizedBox(width: 10),
              Text("MediLoop Privacy Policy", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: AppTheme.textColorPrimary)),
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
                  style: TextStyle(fontSize: 13, height: 1.45, color: AppTheme.textColorSecondary),
                ),
              ],
            ),
          ),
          actions: [
            ElevatedButton(
              onPressed: () {
                setState(() {
                  _agreeToPrivacy = true;
                });
                Navigator.pop(context);
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.primaryColor,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
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
        const SnackBar(content: Text('Passwords do not match'), backgroundColor: Colors.red),
      );
      return;
    }

    setState(() => _isLoading = true);

    final result = await _authService.register(
      name: _nameController.text,
      email: _emailController.text,
      password: _passwordController.text,
      phoneNumber: _phoneController.text,
      age: int.tryParse(_ageController.text) ?? 25,
      gender: _selectedGender ?? 'Other',
      address: _addressController.text,
      city: _cityController.text,
      state: _stateController.text,
      pincode: _pincodeController.text,
      medicalConditions: _selectedConditions,
      allergies: _allergiesController.text,
      emergencyRelationship: _selectedRelationship ?? 'Other',
      emergencyPhone: _emergencyPhoneController.text,
    );

    if (!mounted) return;

    if (result['success'] == true) {
      // Auto-login after registration
      final loginRes = await _authService.login(
        _emailController.text,
        _passwordController.text,
      );
      
      if (!mounted) return;
      setState(() => _isLoading = false);

      if (loginRes['user'] != null) {
        ProfileService().updateUser(loginRes['user']);
      }

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Registration Successful!'), backgroundColor: Colors.green),
      );
      Navigator.pushNamedAndRemoveUntil(context, AppRoutes.home, (route) => false);
    } else {
      setState(() => _isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(result['message'] ?? 'Registration failed'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(AppStrings.register),
        elevation: 0,
        backgroundColor: Colors.transparent,
        foregroundColor: AppTheme.textColorPrimary,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              _buildSectionCard(
                title: "Personal Details",
                children: [
                  CustomTextField(
                    controller: _nameController,
                    labelText: AppStrings.fullName,
                    hintText: "Enter full name",
                    prefixIcon: Icons.person_outline,
                    validator: (v) => v!.isEmpty ? "Required" : null,
                  ),
                  CustomTextField(
                    controller: _phoneController,
                    labelText: AppStrings.mobileNumber,
                    hintText: "Enter 10 digit number",
                    prefixIcon: Icons.phone_android,
                    keyboardType: TextInputType.phone,
                    validator: (v) => (v == null || v.length != 10) ? "Enter 10 digits" : null,
                  ),
                  CustomTextField(
                    controller: _emailController,
                    labelText: AppStrings.email,
                    hintText: "Enter email",
                    prefixIcon: Icons.email_outlined,
                    keyboardType: TextInputType.emailAddress,
                    validator: (v) => (v == null || !v.contains('@')) ? "Invalid email" : null,
                  ),
                  CustomTextField(
                    controller: _passwordController,
                    labelText: AppStrings.password,
                    hintText: "Enter password",
                    prefixIcon: Icons.lock_outline,
                    obscureText: true,
                    validator: (v) => (v == null || v.length < 6) ? "Min 6 chars" : null,
                  ),
                  CustomTextField(
                    controller: _confirmPasswordController,
                    labelText: AppStrings.confirmPassword,
                    hintText: "Confirm password",
                    prefixIcon: Icons.lock_clock_outlined,
                    obscureText: true,
                    validator: (v) => v != _passwordController.text ? "Passwords don't match" : null,
                  ),
                ],
              ),
              _buildSectionCard(
                title: "Basic Information",
                children: [
                  GestureDetector(
                    onTap: () => _selectDob(context),
                    child: AbsorbPointer(
                      child: CustomTextField(
                        controller: _dobController,
                        labelText: "Date of Birth (DD/MM/YYYY)",
                        hintText: "Select your Date of Birth",
                        prefixIcon: Icons.calendar_today_outlined,
                        suffixIcon: const Icon(Icons.arrow_drop_down, color: AppTheme.primaryColor),
                        validator: (v) => v == null || v.isEmpty ? "Please select Date of Birth" : null,
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  CustomTextField(
                    controller: _ageController,
                    labelText: "Calculated Age",
                    hintText: "Calculated automatically from DOB",
                    prefixIcon: Icons.cake_outlined,
                    keyboardType: TextInputType.number,
                    enabled: false,
                    validator: (v) => v == null || v.isEmpty ? "Age required" : null,
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    decoration: const InputDecoration(
                      labelText: AppStrings.gender,
                      prefixIcon: Icon(Icons.people_outline),
                    ),
                    items: ['Male', 'Female', 'Other'].map((String value) {
                      return DropdownMenuItem<String>(
                        value: value,
                        child: Text(value),
                      );
                    }).toList(),
                    onChanged: (v) => setState(() => _selectedGender = v),
                    validator: (v) => v == null ? "Select gender" : null,
                  ),
                ],
              ),
              _buildSectionCard(
                title: "Delivery Address",
                children: [
                  CustomTextField(
                    controller: _addressController,
                    labelText: AppStrings.address,
                    hintText: "Enter address",
                    prefixIcon: Icons.home_outlined,
                    maxLines: 2,
                    validator: (v) => v!.isEmpty ? "Required" : null,
                  ),
                  CustomTextField(
                    controller: _cityController,
                    labelText: AppStrings.city,
                    hintText: "Enter city",
                    prefixIcon: Icons.location_city_outlined,
                    validator: (v) => v!.isEmpty ? "Required" : null,
                  ),
                  CustomTextField(
                    controller: _stateController,
                    labelText: AppStrings.state,
                    hintText: "Enter state",
                    prefixIcon: Icons.map_outlined,
                    validator: (v) => v!.isEmpty ? "Required" : null,
                  ),
                  CustomTextField(
                    controller: _pincodeController,
                    labelText: AppStrings.pincode,
                    hintText: "Enter 6 digit pincode",
                    prefixIcon: Icons.pin_drop_outlined,
                    keyboardType: TextInputType.number,
                    validator: (v) => (v == null || v.length != 6) ? "Invalid pincode" : null,
                  ),
                ],
              ),
              _buildSectionCard(
                title: "Medical Information",
                children: [
                  const Text("Medical Conditions", style: TextStyle(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8.0,
                    children: _medicalConditions.map((condition) {
                      final isSelected = _selectedConditions.contains(condition);
                      return FilterChip(
                        label: Text(condition),
                        selected: isSelected,
                        onSelected: (selected) {
                          setState(() {
                            if (selected) {
                              _selectedConditions.add(condition);
                            } else {
                              _selectedConditions.remove(condition);
                            }
                          });
                        },
                        selectedColor: AppTheme.primaryColor.withOpacity(0.2),
                        checkmarkColor: AppTheme.primaryColor,
                      );
                    }).toList(),
                  ),
                  CustomTextField(
                    controller: _allergiesController,
                    labelText: AppStrings.allergies,
                    hintText: "Enter allergies if any",
                    prefixIcon: Icons.warning_amber_outlined,
                    maxLines: 2,
                  ),
                ],
              ),
              _buildSectionCard(
                title: "Emergency Contact",
                children: [
                  DropdownButtonFormField<String>(
                    decoration: const InputDecoration(
                      labelText: AppStrings.relationship,
                      prefixIcon: Icon(Icons.family_restroom_outlined),
                    ),
                    items: ['Mother', 'Father', 'Brother', 'Sister', 'Spouse', 'Friend', 'Other']
                        .map((String value) {
                      return DropdownMenuItem<String>(
                        value: value,
                        child: Text(value),
                      );
                    }).toList(),
                    onChanged: (v) => setState(() => _selectedRelationship = v),
                    validator: (v) => v == null ? "Select relationship" : null,
                  ),
                  const SizedBox(height: 16),
                  CustomTextField(
                    controller: _emergencyPhoneController,
                    labelText: "Contact Phone Number",
                    hintText: "Enter 10 digit number",
                    prefixIcon: Icons.phone_outlined,
                    keyboardType: TextInputType.phone,
                    validator: (v) => (v == null || v.length != 10) ? "Enter 10 digits" : null,
                  ),
                ],
              ),
              const SizedBox(height: 8),
              CheckboxListTile(
                value: _agreeToPrivacy,
                onChanged: (v) => setState(() => _agreeToPrivacy = v!),
                title: Row(
                  children: [
                    const Text("I agree to the "),
                    GestureDetector(
                      onTap: _showPrivacyPolicyDialog,
                      child: const Text(
                        "Privacy Policy",
                        style: TextStyle(
                          color: AppTheme.primaryColor,
                          fontWeight: FontWeight.bold,
                          decoration: TextDecoration.underline,
                        ),
                      ),
                    ),
                  ],
                ),
                controlAffinity: ListTileControlAffinity.leading,
                activeColor: AppTheme.primaryColor,
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: (_agreeToPrivacy && !_isLoading) ? _register : null,
                child: _isLoading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                      )
                    : const Text(AppStrings.register),
              ),
              const SizedBox(height: 40),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSectionCard({required String title, required List<Widget> children}) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: AppTheme.primaryColor,
              ),
            ),
            const Divider(),
            const SizedBox(height: 8),
            ...children,
          ],
        ),
      ),
    );
  }
}
