import 'package:flutter/material.dart';
import '../../core/constants/app_strings.dart';
import '../../core/theme/app_theme.dart';
import '../../widgets/custom_text_field.dart';

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
  final _addressController = TextEditingController();
  final _cityController = TextEditingController();
  final _stateController = TextEditingController();
  final _pincodeController = TextEditingController();
  final _allergiesController = TextEditingController();
  final _emergencyPhoneController = TextEditingController();

  String? _selectedGender;
  String? _selectedRelationship;
  bool _agreeToPrivacy = false;

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
    _addressController.dispose();
    _cityController.dispose();
    _stateController.dispose();
    _pincodeController.dispose();
    _allergiesController.dispose();
    _emergencyPhoneController.dispose();
    super.dispose();
  }

  void _register() {
    if (_formKey.currentState!.validate() && _agreeToPrivacy) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Registration Successful!')),
      );
      Navigator.pop(context);
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
                  CustomTextField(
                    controller: _ageController,
                    labelText: AppStrings.age,
                    hintText: "Enter age",
                    prefixIcon: Icons.cake_outlined,
                    keyboardType: TextInputType.number,
                    validator: (v) => v!.isEmpty ? "Required" : null,
                  ),
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
                title: const Text(AppStrings.privacyPolicyText),
                controlAffinity: ListTileControlAffinity.leading,
                activeColor: AppTheme.primaryColor,
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: _agreeToPrivacy ? _register : null,
                child: const Text(AppStrings.register),
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
