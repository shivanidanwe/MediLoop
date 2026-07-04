import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../../core/theme/app_theme.dart';
import '../../models/user_model.dart';
import '../../models/address_model.dart';
import '../../models/prescription_model.dart';
import '../../services/profile_service.dart';
import '../../widgets/profile_header.dart';
import '../../widgets/editable_card.dart';
import '../../widgets/address_card.dart';
import '../../widgets/medical_card.dart';
import '../../widgets/settings_tile.dart';
import '../../widgets/prescription_card.dart';
import '../../routes/app_routes.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final ProfileService _profileService = ProfileService();
  late UserModel _user;
  late List<AddressModel> _addresses;
  late List<PrescriptionModel> _prescriptions;

  // Address edit state
  bool _isEditingPrimaryAddress = false;
  final _addressFormKey = GlobalKey<FormState>();
  late TextEditingController _streetController;
  late TextEditingController _cityController;
  late TextEditingController _stateController;
  late TextEditingController _pincodeController;

  // Emergency contact edit state
  bool _isEditingEmergency = false;
  final _emergencyFormKey = GlobalKey<FormState>();
  late TextEditingController _emergencyRelationshipController;
  late TextEditingController _emergencyPhoneController;

  @override
  void initState() {
    super.initState();
    _loadData();
    _profileService.addListener(_onServiceUpdate);

    _streetController = TextEditingController();
    _cityController = TextEditingController();
    _stateController = TextEditingController();
    _pincodeController = TextEditingController();

    _emergencyRelationshipController = TextEditingController(text: _user.emergencyRelationship);
    _emergencyPhoneController = TextEditingController(text: _user.emergencyPhone);
  }

  void _loadData() {
    _user = _profileService.getUser();
    _addresses = _profileService.getAddresses();
    _prescriptions = _profileService.getPrescriptions();
  }

  void _onServiceUpdate() {
    if (mounted) {
      setState(() {
        _loadData();
      });
    }
  }

  @override
  void dispose() {
    _profileService.removeListener(_onServiceUpdate);
    _streetController.dispose();
    _cityController.dispose();
    _stateController.dispose();
    _pincodeController.dispose();
    _emergencyRelationshipController.dispose();
    _emergencyPhoneController.dispose();
    super.dispose();
  }

  // --- Profile Picture Update ---
  void _updateProfilePic(String? path) {
    final updated = _user.copyWith(profilePic: path);
    _profileService.updateUser(updated);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Profile picture updated successfully!')),
    );
  }

  // --- Personal Info Update ---
  void _updatePersonalInfo(UserModel updated) {
    _profileService.updateUser(updated);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Personal details updated successfully!')),
    );
  }

  // --- Primary Address Update (Section 3) ---
  void _startEditingPrimaryAddress() {
    final primaryAddr = _addresses.firstWhere(
      (a) => a.label.toLowerCase() == 'home',
      orElse: () => _addresses.isNotEmpty ? _addresses.first : AddressModel(
        id: 'temp',
        label: 'Home',
        address: '',
        city: '',
        state: '',
        pincode: '',
      ),
    );

    setState(() {
      _streetController.text = primaryAddr.address;
      _cityController.text = primaryAddr.city;
      _stateController.text = primaryAddr.state;
      _pincodeController.text = primaryAddr.pincode;
      _isEditingPrimaryAddress = true;
    });
  }

  void _savePrimaryAddress() {
    if (_addressFormKey.currentState!.validate()) {
      final primaryAddr = _addresses.firstWhere(
        (a) => a.label.toLowerCase() == 'home',
        orElse: () => AddressModel(
          id: '1',
          label: 'Home',
          address: '',
          city: '',
          state: '',
          pincode: '',
        ),
      );

      final updated = primaryAddr.copyWith(
        address: _streetController.text.trim(),
        city: _cityController.text.trim(),
        state: _stateController.text.trim(),
        pincode: _pincodeController.text.trim(),
      );

      if (_addresses.any((a) => a.id == updated.id)) {
        _profileService.updateAddress(updated);
      } else {
        _profileService.addAddress(updated);
      }

      setState(() {
        _isEditingPrimaryAddress = false;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Delivery address saved!')),
      );
    }
  }

  // --- Medical Info Update ---
  void _updateMedicalInfo(List<String> conditions, String allergies) {
    final updated = _user.copyWith(
      medicalConditions: conditions,
      allergies: allergies,
    );
    _profileService.updateUser(updated);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Medical information updated!')),
    );
  }

  // --- Emergency Contact Update ---
  void _saveEmergencyContact() {
    if (_emergencyFormKey.currentState!.validate()) {
      final updated = _user.copyWith(
        emergencyRelationship: _emergencyRelationshipController.text.trim(),
        emergencyPhone: _emergencyPhoneController.text.trim(),
      );
      _profileService.updateUser(updated);
      setState(() {
        _isEditingEmergency = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Emergency contact saved successfully!')),
      );
    }
  }

  // --- Multiple Addresses Management (Section 9) ---
  void _showAddressDialog({AddressModel? addressToEdit}) {
    final isEdit = addressToEdit != null;
    final labelController = TextEditingController(text: isEdit ? addressToEdit.label : 'Home');
    final streetCtrl = TextEditingController(text: isEdit ? addressToEdit.address : '');
    final cityCtrl = TextEditingController(text: isEdit ? addressToEdit.city : '');
    final stateCtrl = TextEditingController(text: isEdit ? addressToEdit.state : '');
    final pincodeCtrl = TextEditingController(text: isEdit ? addressToEdit.pincode : '');
    final formKey = GlobalKey<FormState>();

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          title: Text(isEdit ? "Edit Address" : "Add New Address", style: const TextStyle(fontWeight: FontWeight.bold)),
          content: SingleChildScrollView(
            child: Form(
              key: formKey,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // Label Dropdown
                  DropdownButtonFormField<String>(
                    value: ['Home', 'Office', 'Other'].contains(labelController.text) ? labelController.text : 'Other',
                    items: ['Home', 'Office', 'Other'].map((label) {
                      return DropdownMenuItem(value: label, child: Text(label));
                    }).toList(),
                    onChanged: (val) {
                      if (val != null) labelController.text = val;
                    },
                    decoration: const InputDecoration(labelText: "Label", contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8)),
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: streetCtrl,
                    decoration: const InputDecoration(labelText: "Street Address"),
                    validator: (val) => val == null || val.trim().isEmpty ? "Required" : null,
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: cityCtrl,
                    decoration: const InputDecoration(labelText: "City"),
                    validator: (val) => val == null || val.trim().isEmpty ? "Required" : null,
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: TextFormField(
                          controller: stateCtrl,
                          decoration: const InputDecoration(labelText: "State"),
                          validator: (val) => val == null || val.trim().isEmpty ? "Required" : null,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: TextFormField(
                          controller: pincodeCtrl,
                          keyboardType: TextInputType.number,
                          decoration: const InputDecoration(labelText: "Pincode"),
                          validator: (val) {
                            if (val == null || val.trim().isEmpty) return "Required";
                            if (val.trim().length != 6) return "Should be 6 digits";
                            return null;
                          },
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text("Cancel", style: TextStyle(color: Colors.grey)),
            ),
            ElevatedButton(
              onPressed: () {
                if (formKey.currentState!.validate()) {
                  final newAddr = AddressModel(
                    id: isEdit ? addressToEdit.id : DateTime.now().millisecondsSinceEpoch.toString(),
                    label: labelController.text.trim(),
                    address: streetCtrl.text.trim(),
                    city: cityCtrl.text.trim(),
                    state: stateCtrl.text.trim(),
                    pincode: pincodeCtrl.text.trim(),
                  );
                  if (isEdit) {
                    _profileService.updateAddress(newAddr);
                  } else {
                    _profileService.addAddress(newAddr);
                  }
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text(isEdit ? "Address updated!" : "Address added!")),
                  );
                }
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.primaryColor,
                minimumSize: const Size(100, 40),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
              child: Text(isEdit ? "Update" : "Add"),
            ),
          ],
        );
      },
    );
  }

  void _deleteAddress(AddressModel address) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text("Delete Address"),
          content: Text("Are you sure you want to delete '${address.label}' address?"),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context), child: const Text("Cancel")),
            TextButton(
              onPressed: () {
                _profileService.deleteAddress(address.id);
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Address deleted successfully')),
                );
              },
              child: const Text("Delete", style: TextStyle(color: Colors.red)),
            )
          ],
        );
      },
    );
  }

  // --- Prescription Actions (Section 8) ---
  Future<void> _uploadPrescription() async {
    final ImagePicker picker = ImagePicker();
    try {
      final XFile? image = await picker.pickImage(
        source: ImageSource.gallery,
        imageQuality: 80,
      );
      if (image != null) {
        final prescription = PrescriptionModel(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          uploadDate: DateTime.now().toString().substring(0, 10),
          status: "Pending",
          fileName: image.name,
          filePath: image.path,
        );
        _profileService.addPrescription(prescription);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Prescription uploaded successfully! Placed in verification queue.')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Upload failed: $e')),
      );
    }
  }

  void _viewPrescription(PrescriptionModel rx) {
    showDialog(
      context: context,
      builder: (context) {
        return Dialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              AppBar(
                title: Text(rx.fileName, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                backgroundColor: Colors.transparent,
                elevation: 0,
                leading: IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () => Navigator.pop(context),
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(20.0),
                child: rx.filePath != null
                    ? ClipRRect(
                        borderRadius: BorderRadius.circular(12),
                        child: SizedBox(
                          height: 350,
                          child: Image.file(
                            File(rx.filePath!),
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) => _buildMockRxImage(),
                          ),
                        ),
                      )
                    : _buildMockRxImage(),
              ),
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text("Status: ${rx.status}", style: TextStyle(fontWeight: FontWeight.bold, color: rx.status == 'Verified' ? AppTheme.primaryColor : Colors.orange.shade800)),
                    Text("Date: ${rx.uploadDate}", style: TextStyle(color: Colors.grey.shade600, fontSize: 12)),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildMockRxImage() {
    return Container(
      height: 250,
      width: double.infinity,
      decoration: BoxDecoration(
        color: AppTheme.cardColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.receipt_long_rounded, size: 64, color: AppTheme.primaryColor),
          const SizedBox(height: 12),
          const Text("Prescription Document Scan", style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 4),
          Text("MediLoop AI Pharmacy verification active", style: TextStyle(color: Colors.grey.shade500, fontSize: 11)),
        ],
      ),
    );
  }

  void _deletePrescription(PrescriptionModel rx) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text("Delete Prescription"),
          content: Text("Are you sure you want to delete '${rx.fileName}'?"),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context), child: const Text("Cancel")),
            TextButton(
              onPressed: () {
                _profileService.deletePrescription(rx.id);
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Prescription deleted')),
                );
              },
              child: const Text("Delete", style: TextStyle(color: Colors.red)),
            )
          ],
        );
      },
    );
  }

  // --- Preference Updates (Section 7) ---
  void _updatePreference(String type, bool val) {
    UserModel updated;
    switch (type) {
      case 'push':
        updated = _user.copyWith(pushNotifications: val);
        break;
      case 'email':
        updated = _user.copyWith(emailNotifications: val);
        break;
      case 'sms':
        updated = _user.copyWith(smsNotifications: val);
        break;
      default:
        return;
    }
    _profileService.updateUser(updated);
  }

  // --- Setting Dialogs ---
  void _showChangePasswordDialog() {
    final formKey = GlobalKey<FormState>();
    final oldPasswordController = TextEditingController();
    final newPasswordController = TextEditingController();
    final confirmPasswordController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          title: const Text("Change Password", style: TextStyle(fontWeight: FontWeight.bold)),
          content: Form(
            key: formKey,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextFormField(
                  controller: oldPasswordController,
                  obscureText: true,
                  decoration: const InputDecoration(labelText: "Current Password"),
                  validator: (val) => val == null || val.isEmpty ? "Required" : null,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: newPasswordController,
                  obscureText: true,
                  decoration: const InputDecoration(labelText: "New Password"),
                  validator: (val) {
                    if (val == null || val.isEmpty) return "Required";
                    if (val.length < 6) return "Password must be at least 6 characters";
                    return null;
                  },
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: confirmPasswordController,
                  obscureText: true,
                  decoration: const InputDecoration(labelText: "Confirm New Password"),
                  validator: (val) {
                    if (val == null || val.isEmpty) return "Required";
                    if (val != newPasswordController.text) return "Passwords do not match";
                    return null;
                  },
                ),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context), child: const Text("Cancel")),
            ElevatedButton(
              onPressed: () {
                if (formKey.currentState!.validate()) {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Password updated successfully!')),
                  );
                }
              },
              style: ElevatedButton.styleFrom(backgroundColor: AppTheme.primaryColor),
              child: const Text("Save"),
            ),
          ],
        );
      },
    );
  }

  void _showChangeLanguageDialog() {
    final languages = ["English", "Hindi", "Marathi", "Spanish", "French"];
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          title: const Text("Select Language", style: TextStyle(fontWeight: FontWeight.bold)),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: languages.map((lang) {
              final isSelected = _user.language == lang;
              return RadioListTile<String>(
                value: lang,
                groupValue: _user.language,
                title: Text(lang, style: TextStyle(fontWeight: isSelected ? FontWeight.bold : FontWeight.normal)),
                activeColor: AppTheme.primaryColor,
                onChanged: (val) {
                  if (val != null) {
                    final updated = _user.copyWith(language: val);
                    _profileService.updateUser(updated);
                    Navigator.pop(context);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Language changed to $val')),
                    );
                  }
                },
              );
            }).toList(),
          ),
        );
      },
    );
  }

  void _showAppTextDialog(String title, String content) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
          content: SingleChildScrollView(
            child: Text(
              content,
              style: const TextStyle(fontSize: 13, height: 1.5, color: Colors.black87),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text("Close"),
            )
          ],
        );
      },
    );
  }

  // --- Confirm Logout ---
  void _showLogoutDialog() {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          title: const Text("Logout", style: TextStyle(fontWeight: FontWeight.bold)),
          content: const Text("Are you sure you want to logout?"),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text("Cancel", style: TextStyle(color: Colors.grey)),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context); // Close dialog
                // Navigate to login
                Navigator.pushReplacementNamed(context, AppRoutes.login);
              },
              style: ElevatedButton.styleFrom(backgroundColor: Colors.red.shade700),
              child: const Text("Yes, Logout"),
            )
          ],
        );
      },
    );
  }

  // --- Confirm Delete Account ---
  void _showDeleteAccountDialog() {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          title: Text("Delete Account", style: TextStyle(fontWeight: FontWeight.bold, color: Colors.red.shade700)),
          content: const Text("Warning: Deleting your account will permanently remove all medical data, history, and address details. This action cannot be undone."),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text("Cancel", style: TextStyle(color: Colors.grey)),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                Navigator.pushReplacementNamed(context, AppRoutes.login);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Your account has been deleted successfully.')),
                );
              },
              style: ElevatedButton.styleFrom(backgroundColor: Colors.red.shade700),
              child: const Text("Confirm Delete"),
            )
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text("Profile", style: TextStyle(fontWeight: FontWeight.bold, color: AppTheme.textColorPrimary)),
        backgroundColor: Colors.white,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        physics: const BouncingScrollPhysics(),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
        child: Column(
          children: [
            // 1. Profile Header
            ProfileHeader(
              user: _user,
              onEditPressed: () {
                // Focus/scroll to personal details editable card and make it active
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Scroll down to modify Personal Details!')),
                );
              },
              onImagePicked: _updateProfilePic,
            ),
            const SizedBox(height: 20),

            // 2. Personal Details
            EditableCard(
              user: _user,
              onSave: _updatePersonalInfo,
            ),
            const SizedBox(height: 20),

            // 3. Primary Delivery Address
            _buildPrimaryAddressSection(),
            const SizedBox(height: 20),

            // 4. Medical Information
            MedicalCard(
              user: _user,
              onSave: _updateMedicalInfo,
            ),
            const SizedBox(height: 20),

            // 5. Emergency Contact
            _buildEmergencyContactSection(),
            const SizedBox(height: 20),

            // 7. Order Preferences
            _buildOrderPreferencesSection(),
            const SizedBox(height: 20),

            // 8. Saved Prescriptions
            _buildSavedPrescriptionsSection(),
            const SizedBox(height: 20),

            // 9. Saved Addresses (Multiple addresses list)
            _buildSavedAddressesSection(),
            const SizedBox(height: 20),

            // 6. Account Settings
            _buildAccountSettingsSection(),
            const SizedBox(height: 20),

            // 10. About MediLoop
            _buildAboutMediLoopSection(),
            const SizedBox(height: 28),

            // 11. Logout Button
            _buildLogoutButton(),
            const SizedBox(height: 36),
          ],
        ),
      ),
    );
  }

  // --- Helper Layout Builders ---

  // Section 3: Delivery Address Card
  Widget _buildPrimaryAddressSection() {
    final homeAddress = _addresses.firstWhere(
      (a) => a.label.toLowerCase() == 'home',
      orElse: () => _addresses.isNotEmpty ? _addresses.first : AddressModel(
        id: '1',
        label: 'Home',
        address: 'No Address Set',
        city: 'N/A',
        state: 'N/A',
        pincode: '000000',
      ),
    );

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
        border: Border.all(color: Colors.grey.shade100),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 16, 16, 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: AppTheme.primaryColor.withOpacity(0.08),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: const Icon(
                        Icons.local_shipping_outlined,
                        color: AppTheme.primaryColor,
                        size: 20,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Text(
                      "Delivery Address",
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: AppTheme.textColorPrimary,
                          ),
                    ),
                  ],
                ),
                if (!_isEditingPrimaryAddress)
                  TextButton(
                    onPressed: _startEditingPrimaryAddress,
                    child: const Text("Edit Address", style: TextStyle(color: AppTheme.primaryColor, fontWeight: FontWeight.bold, fontSize: 13)),
                  ),
              ],
            ),
          ),
          const Divider(height: 1, color: Color(0xFFF1F1F1)),
          Padding(
            padding: const EdgeInsets.all(20),
            child: _isEditingPrimaryAddress
                ? Form(
                    key: _addressFormKey,
                    child: Column(
                      children: [
                        TextFormField(
                          controller: _streetController,
                          decoration: const InputDecoration(labelText: "Street Address", hintText: "Flat / Apartment / House No."),
                          validator: (val) => val == null || val.trim().isEmpty ? "Required" : null,
                        ),
                        const SizedBox(height: 12),
                        TextFormField(
                          controller: _cityController,
                          decoration: const InputDecoration(labelText: "City"),
                          validator: (val) => val == null || val.trim().isEmpty ? "Required" : null,
                        ),
                        const SizedBox(height: 12),
                        Row(
                          children: [
                            Expanded(
                              child: TextFormField(
                                controller: _stateController,
                                decoration: const InputDecoration(labelText: "State"),
                                validator: (val) => val == null || val.trim().isEmpty ? "Required" : null,
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: TextFormField(
                                controller: _pincodeController,
                                keyboardType: TextInputType.number,
                                decoration: const InputDecoration(labelText: "Pincode"),
                                validator: (val) {
                                  if (val == null || val.trim().isEmpty) return "Required";
                                  if (val.trim().length != 6) return "Pincode should be 6 digits";
                                  return null;
                                },
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 20),
                        Row(
                          children: [
                            Expanded(
                              child: OutlinedButton(
                                onPressed: () => setState(() => _isEditingPrimaryAddress = false),
                                style: OutlinedButton.styleFrom(
                                  foregroundColor: Colors.grey.shade700,
                                  side: BorderSide(color: Colors.grey.shade300),
                                  padding: const EdgeInsets.symmetric(vertical: 14),
                                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                                ),
                                child: const Text("Cancel"),
                              ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: ElevatedButton(
                                onPressed: _savePrimaryAddress,
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: AppTheme.primaryColor,
                                  padding: const EdgeInsets.symmetric(vertical: 14),
                                  minimumSize: Size.zero,
                                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                                ),
                                child: const Text("Save Address"),
                              ),
                            ),
                          ],
                        )
                      ],
                    ),
                  )
                : Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Icon(Icons.location_on_rounded, color: AppTheme.primaryColor, size: 22),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(homeAddress.label, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                            const SizedBox(height: 4),
                            Text(
                              homeAddress.address,
                              style: TextStyle(color: Colors.grey.shade700, fontSize: 13, height: 1.3),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              "${homeAddress.city}, ${homeAddress.state} - ${homeAddress.pincode}",
                              style: TextStyle(color: Colors.grey.shade500, fontSize: 12),
                            ),
                          ],
                        ),
                      )
                    ],
                  ),
          ),
        ],
      ),
    );
  }

  // Section 5: Emergency Contact Card
  Widget _buildEmergencyContactSection() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
        border: Border.all(color: Colors.grey.shade100),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 16, 16, 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.red.shade50.withOpacity(0.8),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Icon(
                        Icons.contact_emergency_outlined,
                        color: Colors.red.shade800,
                        size: 20,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Text(
                      "Emergency Contact",
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: AppTheme.textColorPrimary,
                          ),
                    ),
                  ],
                ),
                if (!_isEditingEmergency)
                  IconButton(
                    icon: const Icon(Icons.edit_outlined, color: AppTheme.primaryColor),
                    onPressed: () => setState(() => _isEditingEmergency = true),
                  ),
              ],
            ),
          ),
          const Divider(height: 1, color: Color(0xFFF1F1F1)),
          Padding(
            padding: const EdgeInsets.all(20),
            child: _isEditingEmergency
                ? Form(
                    key: _emergencyFormKey,
                    child: Column(
                      children: [
                        TextFormField(
                          controller: _emergencyRelationshipController,
                          decoration: const InputDecoration(labelText: "Relationship (e.g. Spouse, Brother, Parent)"),
                          validator: (val) => val == null || val.trim().isEmpty ? "Relationship required" : null,
                        ),
                        const SizedBox(height: 12),
                        TextFormField(
                          controller: _emergencyPhoneController,
                          keyboardType: TextInputType.phone,
                          decoration: const InputDecoration(labelText: "Phone Number"),
                          validator: (val) {
                            if (val == null || val.trim().isEmpty) return "Phone number required";
                            if (val.trim().replaceAll(RegExp(r'\D'), '').length < 8) return "Enter a valid phone number";
                            return null;
                          },
                        ),
                        const SizedBox(height: 16),
                        Row(
                          children: [
                            Expanded(
                              child: OutlinedButton(
                                onPressed: () {
                                  setState(() {
                                    _isEditingEmergency = false;
                                    _emergencyRelationshipController.text = _user.emergencyRelationship;
                                    _emergencyPhoneController.text = _user.emergencyPhone;
                                  });
                                },
                                style: OutlinedButton.styleFrom(
                                  foregroundColor: Colors.grey.shade700,
                                  side: BorderSide(color: Colors.grey.shade300),
                                  padding: const EdgeInsets.symmetric(vertical: 14),
                                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                                ),
                                child: const Text("Cancel"),
                              ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: ElevatedButton(
                                onPressed: _saveEmergencyContact,
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: AppTheme.primaryColor,
                                  padding: const EdgeInsets.symmetric(vertical: 14),
                                  minimumSize: Size.zero,
                                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                                ),
                                child: const Text("Save Contact"),
                              ),
                            ),
                          ],
                        )
                      ],
                    ),
                  )
                : Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(color: Colors.red.shade50, shape: BoxShape.circle),
                        child: Icon(Icons.phone_in_talk_rounded, color: Colors.red.shade800, size: 20),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              _user.emergencyRelationship,
                              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              _user.emergencyPhone,
                              style: TextStyle(color: Colors.grey.shade600, fontSize: 13, fontWeight: FontWeight.w500),
                            ),
                          ],
                        ),
                      )
                    ],
                  ),
          ),
        ],
      ),
    );
  }

  // Section 7: Order Preferences
  Widget _buildOrderPreferencesSection() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
        border: Border.all(color: Colors.grey.shade100),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 8),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: AppTheme.primaryColor.withOpacity(0.08),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(
                    Icons.notifications_active_outlined,
                    color: AppTheme.primaryColor,
                    size: 20,
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  "Order Preferences",
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.textColorPrimary,
                      ),
                ),
              ],
            ),
          ),
          const Divider(height: 1, color: Color(0xFFF1F1F1)),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 8),
            child: Column(
              children: [
                SwitchListTile(
                  value: _user.pushNotifications,
                  title: const Text("Push Notifications", style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
                  activeColor: AppTheme.primaryColor,
                  onChanged: (val) => _updatePreference('push', val),
                ),
                SwitchListTile(
                  value: _user.emailNotifications,
                  title: const Text("Email Notifications", style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
                  activeColor: AppTheme.primaryColor,
                  onChanged: (val) => _updatePreference('email', val),
                ),
                SwitchListTile(
                  value: _user.smsNotifications,
                  title: const Text("SMS Notifications", style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
                  activeColor: AppTheme.primaryColor,
                  onChanged: (val) => _updatePreference('sms', val),
                ),
              ],
            ),
          )
        ],
      ),
    );
  }

  // Section 8: Saved Prescriptions
  Widget _buildSavedPrescriptionsSection() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
        border: Border.all(color: Colors.grey.shade100),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: AppTheme.primaryColor.withOpacity(0.08),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: const Icon(
                        Icons.description_outlined,
                        color: AppTheme.primaryColor,
                        size: 20,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Text(
                      "Saved Prescriptions",
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: AppTheme.textColorPrimary,
                          ),
                    ),
                  ],
                ),
                ElevatedButton.icon(
                  onPressed: _uploadPrescription,
                  icon: const Icon(Icons.add, size: 16),
                  label: const Text("Upload", style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.primaryColor,
                    minimumSize: Size.zero,
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
              ],
            ),
          ),
          const Divider(height: 1, color: Color(0xFFF1F1F1)),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: _prescriptions.isEmpty
                ? const Center(
                    child: Padding(
                      padding: EdgeInsets.symmetric(vertical: 20),
                      child: Text(
                        "No prescriptions uploaded yet.",
                        style: TextStyle(color: Colors.grey, fontStyle: FontStyle.italic),
                      ),
                    ),
                  )
                : ListView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: _prescriptions.length,
                    itemBuilder: (context, index) {
                      final rx = _prescriptions[index];
                      return PrescriptionCard(
                        prescription: rx,
                        onView: () => _viewPrescription(rx),
                        onDelete: () => _deletePrescription(rx),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }

  // Section 9: Saved Addresses
  Widget _buildSavedAddressesSection() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
        border: Border.all(color: Colors.grey.shade100),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: AppTheme.primaryColor.withOpacity(0.08),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: const Icon(
                        Icons.bookmarks_outlined,
                        color: AppTheme.primaryColor,
                        size: 20,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Text(
                      "Saved Addresses",
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: AppTheme.textColorPrimary,
                          ),
                    ),
                  ],
                ),
                TextButton.icon(
                  onPressed: () => _showAddressDialog(),
                  icon: const Icon(Icons.add, size: 16, color: AppTheme.primaryColor),
                  label: const Text("Add New", style: TextStyle(color: AppTheme.primaryColor, fontWeight: FontWeight.bold, fontSize: 13)),
                  style: TextButton.styleFrom(minimumSize: Size.zero, padding: EdgeInsets.zero),
                ),
              ],
            ),
          ),
          const Divider(height: 1, color: Color(0xFFF1F1F1)),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: _addresses.isEmpty
                ? const Center(
                    child: Padding(
                      padding: EdgeInsets.symmetric(vertical: 16),
                      child: Text("No addresses saved.", style: TextStyle(color: Colors.grey, fontStyle: FontStyle.italic)),
                    ),
                  )
                : ListView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: _addresses.length,
                    itemBuilder: (context, index) {
                      final addr = _addresses[index];
                      // Assume the first Home address or first address in list is default primary
                      final isHome = addr.label.toLowerCase() == 'home';
                      final isDefault = isHome || (_addresses.indexWhere((a) => a.label.toLowerCase() == 'home') == -1 && index == 0);
                      return AddressCard(
                        address: addr,
                        isDefault: isDefault,
                        onEdit: () => _showAddressDialog(addressToEdit: addr),
                        onDelete: () => _deleteAddress(addr),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }

  // Section 6: Account Settings List
  Widget _buildAccountSettingsSection() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
        border: Border.all(color: Colors.grey.shade100),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 8),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: AppTheme.primaryColor.withOpacity(0.08),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(
                    Icons.settings_outlined,
                    color: AppTheme.primaryColor,
                    size: 20,
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  "Account Settings",
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.textColorPrimary,
                      ),
                ),
              ],
            ),
          ),
          const Divider(height: 1, color: Color(0xFFF1F1F1)),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              children: [
                SettingsTile(
                  leadingIcon: Icons.lock_outline_rounded,
                  title: "Change Password",
                  subtitle: "Update your login password",
                  onTap: _showChangePasswordDialog,
                ),
                SettingsTile(
                  leadingIcon: Icons.translate_rounded,
                  title: "Change Language",
                  subtitle: "Current: ${_user.language}",
                  onTap: _showChangeLanguageDialog,
                ),
                SettingsTile(
                  leadingIcon: Icons.dark_mode_outlined,
                  title: "Dark Mode Toggle",
                  subtitle: _user.darkMode ? "Enabled" : "Disabled",
                  trailing: Switch(
                    value: _user.darkMode,
                    activeColor: AppTheme.primaryColor,
                    onChanged: (val) {
                      _profileService.updateUser(_user.copyWith(darkMode: val));
                    },
                  ),
                ),
                SettingsTile(
                  leadingIcon: Icons.policy_outlined,
                  title: "Privacy Policy",
                  onTap: () => _showAppTextDialog("Privacy Policy", "At MediLoop, your medical privacy is of paramount importance. This policy outlines how our autonomous pharmacy system processes data. All prescriptions uploaded are stored in encrypted, HIPAA-compliant databases. We use AI diagnostic scanners and verification models to analyze documents to prevent prescription misuse. We do not sell or lease patient records to third-party marketing brokers. You can request record purging at any time through our customer support desk."),
                ),
                SettingsTile(
                  leadingIcon: Icons.gavel_outlined,
                  title: "Terms & Conditions",
                  onTap: () => _showAppTextDialog("Terms & Conditions", "Welcome to MediLoop. By using our application, you agree to comply with our Terms of Service. MediLoop provides an AI-driven online storefront that interacts with licensed pharmacy centers. All orders made via text or voice are subjected to review by registered pharmacists. MediLoop does not issue prescriptions directly; you must provide valid prescription documentation for all controlled drugs. In case of medical emergencies, please dial emergency phone numbers immediately instead of placing medication requests on this app."),
                ),
                SettingsTile(
                  leadingIcon: Icons.delete_forever_outlined,
                  iconColor: Colors.red.shade700,
                  title: "Delete Account",
                  textColor: Colors.red.shade700,
                  subtitle: "Permanently erase your MediLoop account",
                  onTap: _showDeleteAccountDialog,
                ),
              ],
            ),
          )
        ],
      ),
    );
  }

  // Section 10: About MediLoop Card
  Widget _buildAboutMediLoopSection() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppTheme.cardColor,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.grey.shade100),
      ),
      child: Column(
        children: [
          Row(
            children: [
              // Logo placeholder
              Container(
                width: 50,
                height: 50,
                decoration: BoxDecoration(
                  color: AppTheme.primaryColor.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: AppTheme.primaryColor.withOpacity(0.2), width: 1.5),
                ),
                child: const Icon(Icons.blur_circular_rounded, color: AppTheme.primaryColor, size: 32),
              ),
              const SizedBox(width: 14),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "MediLoop",
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 18,
                        color: AppTheme.primaryColor,
                        letterSpacing: 0.5,
                      ),
                    ),
                    SizedBox(height: 2),
                    Text(
                      "Version 1.0.0",
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              )
            ],
          ),
          const SizedBox(height: 14),
          Text(
            "MediLoop is an AI-powered autonomous pharmacy platform that enables customers to order medicines using voice or text, upload prescriptions, receive intelligent refill reminders, and experience seamless AI-assisted pharmacy services.",
            style: TextStyle(
              fontSize: 12,
              height: 1.4,
              color: Colors.grey.shade700,
            ),
          ),
          const Divider(height: 24, color: Colors.black12),
          // Actions Buttons Grid
          Wrap(
            spacing: 12,
            runSpacing: 10,
            alignment: WrapAlignment.center,
            children: [
              _buildAboutButton(Icons.support_agent_rounded, "Contact Support", () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Connecting to MediLoop AI Support Desk...')),
                );
              }),
              _buildAboutButton(Icons.star_rate_rounded, "Rate App", () {
                _showRatingDialog();
              }),
              _buildAboutButton(Icons.share_rounded, "Share App", () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Generative invitation link copied to clipboard!')),
                );
              }),
            ],
          )
        ],
      ),
    );
  }

  Widget _buildAboutButton(IconData icon, String label, VoidCallback onPressed) {
    return ActionChip(
      onPressed: onPressed,
      avatar: Icon(icon, size: 14, color: AppTheme.primaryColor),
      label: Text(label, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppTheme.primaryColor)),
      backgroundColor: Colors.white,
      side: BorderSide(color: AppTheme.primaryColor.withOpacity(0.3)),
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
    );
  }

  void _showRatingDialog() {
    int rating = 5;
    showDialog(
      context: context,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AlertDialog(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
              title: const Text("Rate MediLoop", style: TextStyle(fontWeight: FontWeight.bold), textAlign: TextAlign.center),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text("How has your autonomous pharmacy experience been?", textAlign: TextAlign.center, style: TextStyle(fontSize: 13)),
                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: List.generate(5, (index) {
                      final starIndex = index + 1;
                      return IconButton(
                        icon: Icon(
                          starIndex <= rating ? Icons.star_rounded : Icons.star_outline_rounded,
                          color: Colors.amber.shade700,
                          size: 32,
                        ),
                        onPressed: () {
                          setDialogState(() {
                            rating = starIndex;
                          });
                        },
                      );
                    }),
                  ),
                ],
              ),
              actions: [
                TextButton(onPressed: () => Navigator.pop(context), child: const Text("Cancel")),
                ElevatedButton(
                  onPressed: () {
                    Navigator.pop(context);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Thank you for rating us $rating stars!')),
                    );
                  },
                  style: ElevatedButton.styleFrom(backgroundColor: AppTheme.primaryColor),
                  child: const Text("Submit"),
                )
              ],
            );
          },
        );
      },
    );
  }

  // Section 11: Logout button
  Widget _buildLogoutButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton.icon(
        onPressed: _showLogoutDialog,
        icon: const Icon(Icons.logout_rounded, size: 20),
        label: const Text("Log Out"),
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.red.shade700,
          foregroundColor: Colors.white,
          elevation: 1,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          padding: const EdgeInsets.symmetric(vertical: 16),
        ),
      ),
    );
  }
}
