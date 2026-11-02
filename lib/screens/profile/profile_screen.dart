import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../../core/theme/app_theme.dart';
import '../../models/user_model.dart';
import '../../models/address_model.dart';
import '../../models/prescription_model.dart';
import '../../services/profile_service.dart';
import '../../services/auth_service.dart';
import '../../services/cart_service.dart';
import '../../core/constants/api_config.dart';
import '../../widgets/profile_header.dart';
import '../../widgets/editable_card.dart';
import '../../widgets/address_card.dart';
import '../../widgets/medical_card.dart';
import '../../widgets/settings_tile.dart';
import '../../widgets/prescription_card.dart';
import '../../routes/app_routes.dart';

class ProfileScreen extends StatefulWidget {
  final VoidCallback? onBackToHome;
  const ProfileScreen({super.key, this.onBackToHome});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final ProfileService _profileService = ProfileService();
  late UserModel _user;
  late List<AddressModel> _addresses;
  late List<PrescriptionModel> _prescriptions;

  bool _showAllOrders = false;
  bool _showAllPrescriptions = false;
  static const int _historyDisplayLimit = 4;

  bool _isFetchingProfile = false;

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
    CartService().addListener(_onServiceUpdate);
    CartService().fetchOrdersFromBackend();

    _streetController = TextEditingController();
    _cityController = TextEditingController();
    _stateController = TextEditingController();
    _pincodeController = TextEditingController();

    _emergencyRelationshipController = TextEditingController(text: _user.emergencyRelationship);
    _emergencyPhoneController = TextEditingController(text: _user.emergencyPhone);

    if (_user.name.isEmpty) {
      _fetchProfileFromServer();
    }
  }

  void _fetchProfileFromServer() async {
    setState(() {
      _isFetchingProfile = true;
    });
    await _profileService.fetchProfileFromServer();
    if (mounted) {
      setState(() {
        _isFetchingProfile = false;
        _emergencyRelationshipController.text = _user.emergencyRelationship;
        _emergencyPhoneController.text = _user.emergencyPhone;
      });
    }
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
    CartService().removeListener(_onServiceUpdate);
    _streetController.dispose();
    _cityController.dispose();
    _stateController.dispose();
    _pincodeController.dispose();
    _emergencyRelationshipController.dispose();
    _emergencyPhoneController.dispose();
    super.dispose();
  }

  void _updateProfilePic(String? path) async {
    final updated = _user.copyWith(profilePic: path);
    await _profileService.updateUser(updated);
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Profile picture stored in database!')),
      );
    }
  }

  void _updatePersonalInfo(UserModel updated) async {
    await _profileService.updateUser(updated);
    if (mounted) {
      setState(() {
        _user = _profileService.getUser();
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Personal details updated & stored in database!')),
      );
    }
  }

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

  void _savePrimaryAddress() async {
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
        await _profileService.updateAddress(updated);
      } else {
        await _profileService.addAddress(updated);
      }

      if (mounted) {
        setState(() {
          _isEditingPrimaryAddress = false;
          _loadData();
        });

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Delivery address saved & stored in database!')),
        );
      }
    }
  }

  void _updateMedicalInfo(List<String> conditions, String allergies) async {
    final updated = _user.copyWith(
      medicalConditions: conditions,
      allergies: allergies,
    );
    await _profileService.updateUser(updated);
    if (mounted) {
      setState(() {
        _user = _profileService.getUser();
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Medical information stored in database!')),
      );
    }
  }

  void _saveEmergencyContact() async {
    if (_emergencyFormKey.currentState!.validate()) {
      final updated = _user.copyWith(
        emergencyRelationship: _emergencyRelationshipController.text.trim(),
        emergencyPhone: _emergencyPhoneController.text.trim(),
      );
      await _profileService.updateUser(updated);
      if (mounted) {
        setState(() {
          _isEditingEmergency = false;
          _user = _profileService.getUser();
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Emergency contact saved to database!')),
        );
      }
    }
  }

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
          backgroundColor: Colors.white,
          surfaceTintColor: Colors.transparent,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
          title: Text(isEdit ? "Edit Address" : "Add New Address", style: const TextStyle(fontWeight: FontWeight.bold, color: AppTheme.textColorPrimary)),
          content: SingleChildScrollView(
            child: Form(
              key: formKey,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  DropdownButtonFormField<String>(
                    initialValue: ['Home', 'Office', 'Other'].contains(labelController.text) ? labelController.text : 'Other',
                    items: ['Home', 'Office', 'Other'].map((label) {
                      return DropdownMenuItem(value: label, child: Text(label));
                    }).toList(),
                    onChanged: (val) {
                      if (val != null) labelController.text = val;
                    },
                    decoration: const InputDecoration(labelText: "Label"),
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
                            if (val.trim().length != 6) return "6 digits";
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
              child: const Text("Cancel", style: TextStyle(color: AppTheme.textColorSecondary, fontWeight: FontWeight.bold)),
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
                minimumSize: const Size(100, 44),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
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
          backgroundColor: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          title: const Text("Delete Address", style: TextStyle(fontWeight: FontWeight.bold)),
          content: Text("Are you sure you want to delete '${address.label}' address?"),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context), child: const Text("Cancel", style: TextStyle(color: AppTheme.textColorSecondary))),
            TextButton(
              onPressed: () {
                _profileService.deleteAddress(address.id);
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Address deleted successfully')),
                );
              },
              child: const Text("Delete", style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold)),
            )
          ],
        );
      },
    );
  }

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

  String _getPrescriptionImageUrl(String? rawPath) {
    if (rawPath == null || rawPath.trim().isEmpty) return '';
    if (rawPath.startsWith('http://') || rawPath.startsWith('https://')) return rawPath;
    String clean = rawPath.replaceAll(r'\', '/');
    if (clean.contains('uploads/')) {
      clean = clean.substring(clean.indexOf('uploads/'));
    }
    if (!clean.startsWith('/')) {
      clean = '/$clean';
    }
    final base = ApiConfig.baseUrl.replaceAll('/api/v1', '');
    return '$base$clean';
  }

  Widget _buildPrescriptionImage(PrescriptionModel rx) {
    final url = _getPrescriptionImageUrl(rx.filePath);
    if (url.isNotEmpty) {
      return ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: Container(
          constraints: const BoxConstraints(maxHeight: 280),
          width: double.infinity,
          color: Colors.black.withOpacity(0.04),
          child: Image.network(
            url,
            fit: BoxFit.contain,
            loadingBuilder: (context, child, progress) {
              if (progress == null) return child;
              return const SizedBox(
                height: 160,
                child: Center(
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              );
            },
            errorBuilder: (context, error, stackTrace) => _buildMockRxImage(),
          ),
        ),
      );
    }
    return _buildMockRxImage();
  }

  void _viewPrescription(PrescriptionModel rx) {
    showDialog(
      context: context,
      builder: (context) {
        return Dialog(
          backgroundColor: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 500, maxHeight: 650),
            child: SingleChildScrollView(
              physics: const BouncingScrollPhysics(),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  AppBar(
                    title: Text(
                      rx.fileName,
                      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.textColorPrimary),
                      overflow: TextOverflow.ellipsis,
                    ),
                    backgroundColor: Colors.transparent,
                    elevation: 0,
                    leading: IconButton(
                      icon: const Icon(Icons.close, color: AppTheme.textColorPrimary),
                      onPressed: () => Navigator.pop(context),
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 20.0),
                    child: _buildPrescriptionImage(rx),
                  ),
                  const SizedBox(height: 16),

                  // Extracted Medicines structured list if available
                  if (rx.items.isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 20.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              const Icon(Icons.medication_rounded, size: 16, color: AppTheme.primaryColor),
                              const SizedBox(width: 6),
                              Text(
                                "Extracted Medicines (${rx.items.length})",
                                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: AppTheme.textColorPrimary),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          ...rx.items.map((it) {
                            final name = (it['medicine_name'] ?? it['name'] ?? 'Prescribed Medicine').toString();
                            final strength = (it['strength'] ?? '').toString();
                            final dosage = (it['dosage_pattern'] ?? it['dosage'] ?? '').toString();
                            final qty = (it['calculated_quantity'] ?? it['quantity'] ?? '').toString();

                            return Container(
                              margin: const EdgeInsets.only(bottom: 6),
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                              decoration: BoxDecoration(
                                color: AppTheme.backgroundColor,
                                borderRadius: BorderRadius.circular(10),
                                border: Border.all(color: Colors.grey.shade200),
                              ),
                              child: Row(
                                children: [
                                  const Icon(Icons.check_circle_outline_rounded, size: 14, color: AppTheme.primaryColor),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      "$name ${strength.isNotEmpty ? '• $strength' : ''} ${dosage.isNotEmpty ? '• $dosage' : ''}",
                                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppTheme.textColorPrimary),
                                    ),
                                  ),
                                  if (qty.isNotEmpty)
                                    Text("Qty: $qty", style: const TextStyle(fontSize: 11, color: AppTheme.textColorSecondary, fontWeight: FontWeight.bold)),
                                ],
                              ),
                            );
                          }),
                          const SizedBox(height: 12),
                        ],
                      ),
                    ),

                  // Extracted Text section
                  if (rx.extractedText != null && rx.extractedText!.isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.fromLTRB(20, 0, 20, 16),
                      child: Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: AppTheme.backgroundColor,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: AppTheme.primaryColor.withOpacity(0.15)),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Row(
                              children: [
                                Icon(Icons.receipt_long_rounded, size: 16, color: AppTheme.primaryColor),
                                SizedBox(width: 6),
                                Text(
                                  "OCR Extracted Text",
                                  style: TextStyle(
                                    fontSize: 12,
                                    fontWeight: FontWeight.bold,
                                    color: AppTheme.textColorPrimary,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 6),
                            Text(
                              rx.extractedText!,
                              style: const TextStyle(
                                fontSize: 11.5,
                                height: 1.4,
                                color: AppTheme.textColorPrimary,
                              ),
                            ),
                          ],
                        ),
                      ),
                    )
                  else
                    Padding(
                      padding: const EdgeInsets.fromLTRB(20, 0, 20, 16),
                      child: Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.amber.shade50,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: Colors.amber.shade200),
                        ),
                        child: const Row(
                          children: [
                            Icon(Icons.info_outline_rounded, size: 16, color: Colors.orange),
                            SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                "No medicines could be auto-extracted. Prescriptions without clear text are forwarded to the pharmacist for manual review.",
                                style: TextStyle(fontSize: 11.5, color: Colors.brown),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),

                  Padding(
                    padding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: (rx.status.toLowerCase().contains('verif') || rx.status.toLowerCase().contains('approv')
                                    ? const Color(0xFF2E7D32)
                                    : Colors.orange.shade800)
                                .withOpacity(0.12),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            "Status: ${rx.status}",
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 11,
                              color: (rx.status.toLowerCase().contains('verif') || rx.status.toLowerCase().contains('approv')
                                  ? const Color(0xFF2E7D32)
                                  : Colors.orange.shade800),
                            ),
                          ),
                        ),
                        Text("Uploaded: ${rx.uploadDate}", style: const TextStyle(color: AppTheme.textColorSecondary, fontSize: 11.5)),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildMockRxImage() {
    return Container(
      height: 240,
      width: double.infinity,
      decoration: BoxDecoration(
        color: AppTheme.backgroundColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: const Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.receipt_long_rounded, size: 54, color: AppTheme.primaryColor),
          SizedBox(height: 12),
          Text("Prescription Document Scan", style: TextStyle(fontWeight: FontWeight.bold, color: AppTheme.textColorPrimary)),
          SizedBox(height: 4),
          Text("MediLoop AI Pharmacy verification active", style: TextStyle(color: AppTheme.textColorSecondary, fontSize: 11.5)),
        ],
      ),
    );
  }

  void _deletePrescription(PrescriptionModel rx) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          backgroundColor: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          title: const Text("Delete Prescription", style: TextStyle(fontWeight: FontWeight.bold)),
          content: Text("Are you sure you want to delete '${rx.fileName}'?"),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context), child: const Text("Cancel", style: TextStyle(color: AppTheme.textColorSecondary))),
            TextButton(
              onPressed: () {
                _profileService.deletePrescription(rx.id);
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Prescription deleted')),
                );
              },
              child: const Text("Delete", style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold)),
            )
          ],
        );
      },
    );
  }

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

  void _showLogoutDialog() {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          backgroundColor: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
          title: const Text("Logout", style: TextStyle(fontWeight: FontWeight.bold, color: AppTheme.textColorPrimary)),
          content: const Text("Are you sure you want to logout?"),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text("Cancel", style: TextStyle(color: AppTheme.textColorSecondary, fontWeight: FontWeight.bold)),
            ),
            ElevatedButton(
              onPressed: () async {
                Navigator.pop(context);
                await AuthService().logout();
                if (context.mounted) {
                  Navigator.pushNamedAndRemoveUntil(context, AppRoutes.login, (route) => false);
                }
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red.shade700,
                minimumSize: const Size(110, 44),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              child: const Text("Yes, Logout"),
            )
          ],
        );
      },
    );
  }

  void _handleBackNavigation() {
    if (widget.onBackToHome != null) {
      widget.onBackToHome!();
    } else if (Navigator.canPop(context)) {
      Navigator.pop(context);
    } else {
      Navigator.pushReplacementNamed(context, AppRoutes.home);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isFetchingProfile) {
      return PopScope(
        canPop: false,
        onPopInvokedWithResult: (didPop, _) {
          if (!didPop) _handleBackNavigation();
        },
        child: Scaffold(
          backgroundColor: AppTheme.backgroundColor,
          appBar: AppBar(
            title: const Text("My Profile", style: TextStyle(fontWeight: FontWeight.bold, color: AppTheme.textColorPrimary)),
            elevation: 0,
            backgroundColor: Colors.transparent,
            centerTitle: true,
            leading: IconButton(
              icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 18, color: AppTheme.textColorPrimary),
              onPressed: _handleBackNavigation,
            ),
          ),
          body: const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                CircularProgressIndicator(valueColor: AlwaysStoppedAnimation<Color>(AppTheme.primaryColor)),
                SizedBox(height: 16),
                Text("Loading profile data from API...", style: TextStyle(color: AppTheme.textColorSecondary, fontWeight: FontWeight.w500)),
              ],
            ),
          ),
        ),
      );
    }

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, _) {
        if (!didPop) _handleBackNavigation();
      },
      child: Scaffold(
        backgroundColor: AppTheme.backgroundColor,
        appBar: AppBar(
          title: const Text("My Profile", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: AppTheme.textColorPrimary)),
          backgroundColor: Colors.transparent,
          surfaceTintColor: Colors.transparent,
          elevation: 0,
          centerTitle: true,
          leading: IconButton(
            icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 18, color: AppTheme.textColorPrimary),
            onPressed: _handleBackNavigation,
          ),
        ),
        body: SingleChildScrollView(
        physics: const BouncingScrollPhysics(),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
        child: Column(
          children: [
            // 1. Profile Header
            ProfileHeader(
              user: _user,
              onEditPressed: () {
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

            // Order History (Persistent order tracking)
            _buildOrderHistorySection(),
            const SizedBox(height: 20),

            // 8. Saved Prescriptions
            _buildSavedPrescriptionsSection(),
            const SizedBox(height: 20),

            // 9. Saved Addresses
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
    ),
  );
}

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
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.015),
            blurRadius: 12,
            offset: const Offset(0, 6),
          ),
        ],
        border: Border.all(color: const Color(0xFFE5E7EB).withOpacity(0.5), width: 1),
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
                        color: AppTheme.secondaryColor.withOpacity(0.4),
                        shape: BoxShape.circle,
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
                            fontSize: 15.5,
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
          const Divider(height: 1, thickness: 0.5),
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
                                  foregroundColor: AppTheme.textColorSecondary,
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
                            Text(homeAddress.label, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14.5, color: AppTheme.textColorPrimary)),
                            const SizedBox(height: 4),
                            Text(
                              homeAddress.address,
                              style: const TextStyle(color: AppTheme.textColorSecondary, fontSize: 13, height: 1.35),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              "${homeAddress.city}, ${homeAddress.state} - ${homeAddress.pincode}",
                              style: TextStyle(color: AppTheme.textColorSecondary.withOpacity(0.8), fontSize: 12),
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

  Widget _buildEmergencyContactSection() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.015),
            blurRadius: 12,
            offset: const Offset(0, 6),
          ),
        ],
        border: Border.all(color: const Color(0xFFE5E7EB).withOpacity(0.5), width: 1),
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
                        color: Colors.red.shade50,
                        shape: BoxShape.circle,
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
                            fontSize: 15.5,
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
          const Divider(height: 1, thickness: 0.5),
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
                                  foregroundColor: AppTheme.textColorSecondary,
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
                              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: AppTheme.textColorPrimary),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              _user.emergencyPhone,
                              style: const TextStyle(color: AppTheme.textColorSecondary, fontSize: 13, fontWeight: FontWeight.w500),
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

  Widget _buildOrderPreferencesSection() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.015),
            blurRadius: 12,
            offset: const Offset(0, 6),
          ),
        ],
        border: Border.all(color: const Color(0xFFE5E7EB).withOpacity(0.5), width: 1),
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
                    color: AppTheme.secondaryColor.withOpacity(0.4),
                    shape: BoxShape.circle,
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
                        fontSize: 15.5,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.textColorPrimary,
                      ),
                ),
              ],
            ),
          ),
          const Divider(height: 1, thickness: 0.5),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 8),
            child: Column(
              children: [
                SwitchListTile(
                  value: _user.pushNotifications,
                  title: const Text("Push Notifications", style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500, color: AppTheme.textColorPrimary)),
                  activeColor: AppTheme.primaryColor,
                  onChanged: (val) => _updatePreference('push', val),
                ),
                SwitchListTile(
                  value: _user.emailNotifications,
                  title: const Text("Email Notifications", style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500, color: AppTheme.textColorPrimary)),
                  activeColor: AppTheme.primaryColor,
                  onChanged: (val) => _updatePreference('email', val),
                ),
                SwitchListTile(
                  value: _user.smsNotifications,
                  title: const Text("SMS Notifications", style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500, color: AppTheme.textColorPrimary)),
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

  Widget _buildOrderHistorySection() {
    final orders = CartService().orders;
    final displayedOrders = _showAllOrders ? orders : orders.take(_historyDisplayLimit).toList();
    final hasMoreOrders = orders.length > _historyDisplayLimit;

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.015),
            blurRadius: 12,
            offset: const Offset(0, 6),
          ),
        ],
        border: Border.all(color: const Color(0xFFE5E7EB).withOpacity(0.5), width: 1),
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
                        color: AppTheme.secondaryColor.withOpacity(0.4),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.shopping_bag_outlined,
                        color: AppTheme.primaryColor,
                        size: 20,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Text(
                      "Order History (${orders.length})",
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontSize: 15.5,
                            fontWeight: FontWeight.bold,
                            color: AppTheme.textColorPrimary,
                          ),
                    ),
                  ],
                ),
                TextButton(
                  onPressed: () => CartService().fetchOrdersFromBackend(),
                  child: const Text("Refresh", style: TextStyle(color: AppTheme.primaryColor, fontWeight: FontWeight.bold, fontSize: 12.5)),
                ),
              ],
            ),
          ),
          const Divider(height: 1, thickness: 0.5),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: orders.isEmpty
                ? const Center(
                    child: Padding(
                      padding: EdgeInsets.symmetric(vertical: 20),
                      child: Text(
                        "No orders placed yet.",
                        style: TextStyle(color: AppTheme.textColorSecondary, fontStyle: FontStyle.italic),
                      ),
                    ),
                  )
                : Column(
                    children: [
                      ListView.builder(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        itemCount: displayedOrders.length,
                        itemBuilder: (context, index) {
                          final order = displayedOrders[index];
                          Color statusColor;
                          switch (order.status.toLowerCase()) {
                            case 'delivered':
                              statusColor = const Color(0xFF2E7D32);
                              break;
                            case 'prescription approved':
                              statusColor = Colors.teal.shade700;
                              break;
                            case 'out for delivery':
                              statusColor = Colors.blue.shade700;
                              break;
                            case 'preparing':
                            case 'preparing order':
                              statusColor = Colors.indigo.shade700;
                              break;
                            case 'cancelled':
                              statusColor = Colors.red.shade700;
                              break;
                            default:
                              statusColor = Colors.orange.shade800;
                          }

                          final dateStr = "${order.orderDate.day.toString().padLeft(2, '0')}/${order.orderDate.month.toString().padLeft(2, '0')}/${order.orderDate.year}";

                          return Container(
                            margin: const EdgeInsets.only(bottom: 12),
                            padding: const EdgeInsets.all(14),
                            decoration: BoxDecoration(
                              color: AppTheme.backgroundColor,
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(color: Colors.grey.shade200),
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Row(
                                      children: [
                                        const Icon(Icons.receipt_outlined, size: 16, color: AppTheme.primaryColor),
                                        const SizedBox(width: 6),
                                        Text(
                                          order.orderId,
                                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: AppTheme.textColorPrimary),
                                        ),
                                      ],
                                    ),
                                    Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                      decoration: BoxDecoration(
                                        color: statusColor.withOpacity(0.12),
                                        borderRadius: BorderRadius.circular(8),
                                      ),
                                      child: Text(
                                        order.status,
                                        style: TextStyle(
                                          color: statusColor,
                                          fontWeight: FontWeight.bold,
                                          fontSize: 10.5,
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 6),
                                Text(
                                  "Placed on $dateStr • ${order.items.length} ${order.items.length == 1 ? 'medicine' : 'medicines'}",
                                  style: const TextStyle(color: AppTheme.textColorSecondary, fontSize: 11.5),
                                ),
                                if (order.prescriptionId != null) ...[
                                  const SizedBox(height: 4),
                                  Row(
                                    children: [
                                      const Icon(Icons.assignment_outlined, size: 12, color: Color(0xFF2E7D32)),
                                      const SizedBox(width: 4),
                                      Text(
                                        "Linked to Prescription #${order.prescriptionId}",
                                        style: const TextStyle(fontSize: 11, color: Color(0xFF2E7D32), fontWeight: FontWeight.w600),
                                      ),
                                    ],
                                  ),
                                ],
                                const Divider(height: 16, thickness: 0.5),
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Text(
                                      "Total: ₹${order.grandTotal.toStringAsFixed(2)}",
                                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14.5, color: AppTheme.primaryColor),
                                    ),
                                    ElevatedButton.icon(
                                      onPressed: () {
                                        Navigator.pushNamed(
                                          context,
                                          AppRoutes.orderTracking,
                                          arguments: order.orderId,
                                        );
                                      },
                                      style: ElevatedButton.styleFrom(
                                        backgroundColor: AppTheme.primaryColor,
                                        minimumSize: Size.zero,
                                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
                                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                                      ),
                                      icon: const Icon(Icons.location_on_outlined, size: 13, color: Colors.white),
                                      label: const Text("Track Order", style: TextStyle(color: Colors.white, fontSize: 11.5, fontWeight: FontWeight.bold)),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          );
                        },
                      ),
                      if (hasMoreOrders) ...[
                        const SizedBox(height: 6),
                        SizedBox(
                          width: double.infinity,
                          child: OutlinedButton.icon(
                            onPressed: () {
                              setState(() {
                                _showAllOrders = !_showAllOrders;
                              });
                            },
                            icon: Icon(
                              _showAllOrders ? Icons.keyboard_arrow_up_rounded : Icons.keyboard_arrow_down_rounded,
                              size: 18,
                              color: AppTheme.primaryColor,
                            ),
                            label: Text(
                              _showAllOrders
                                  ? "View Less"
                                  : "View More (${orders.length - _historyDisplayLimit} more ${orders.length - _historyDisplayLimit == 1 ? 'order' : 'orders'})",
                              style: const TextStyle(
                                color: AppTheme.primaryColor,
                                fontWeight: FontWeight.bold,
                                fontSize: 13,
                              ),
                            ),
                            style: OutlinedButton.styleFrom(
                              side: BorderSide(color: AppTheme.primaryColor.withOpacity(0.35)),
                              backgroundColor: AppTheme.primaryColor.withOpacity(0.05),
                              padding: const EdgeInsets.symmetric(vertical: 10),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            ),
                          ),
                        ),
                      ],
                    ],
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildSavedPrescriptionsSection() {
    final displayedPrescriptions = _showAllPrescriptions
        ? _prescriptions
        : _prescriptions.take(_historyDisplayLimit).toList();
    final hasMorePrescriptions = _prescriptions.length > _historyDisplayLimit;

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.015),
            blurRadius: 12,
            offset: const Offset(0, 6),
          ),
        ],
        border: Border.all(color: const Color(0xFFE5E7EB).withOpacity(0.5), width: 1),
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
                        color: AppTheme.secondaryColor.withOpacity(0.4),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.description_outlined,
                        color: AppTheme.primaryColor,
                        size: 20,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Text(
                      "Prescription History (${_prescriptions.length})",
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontSize: 15.5,
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
          const Divider(height: 1, thickness: 0.5),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: _prescriptions.isEmpty
                ? const Center(
                    child: Padding(
                      padding: EdgeInsets.symmetric(vertical: 20),
                      child: Text(
                        "No prescriptions uploaded yet.",
                        style: TextStyle(color: AppTheme.textColorSecondary, fontStyle: FontStyle.italic),
                      ),
                    ),
                  )
                : Column(
                    children: [
                      ListView.builder(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        itemCount: displayedPrescriptions.length,
                        itemBuilder: (context, index) {
                          final rx = displayedPrescriptions[index];
                          return PrescriptionCard(
                            prescription: rx,
                            onView: () => _viewPrescription(rx),
                            onDelete: () => _deletePrescription(rx),
                          );
                        },
                      ),
                      if (hasMorePrescriptions) ...[
                        const SizedBox(height: 6),
                        SizedBox(
                          width: double.infinity,
                          child: OutlinedButton.icon(
                            onPressed: () {
                              setState(() {
                                _showAllPrescriptions = !_showAllPrescriptions;
                              });
                            },
                            icon: Icon(
                              _showAllPrescriptions ? Icons.keyboard_arrow_up_rounded : Icons.keyboard_arrow_down_rounded,
                              size: 18,
                              color: AppTheme.primaryColor,
                            ),
                            label: Text(
                              _showAllPrescriptions
                                  ? "View Less"
                                  : "View More (${_prescriptions.length - _historyDisplayLimit} more ${_prescriptions.length - _historyDisplayLimit == 1 ? 'prescription' : 'prescriptions'})",
                              style: const TextStyle(
                                color: AppTheme.primaryColor,
                                fontWeight: FontWeight.bold,
                                fontSize: 13,
                              ),
                            ),
                            style: OutlinedButton.styleFrom(
                              side: BorderSide(color: AppTheme.primaryColor.withOpacity(0.35)),
                              backgroundColor: AppTheme.primaryColor.withOpacity(0.05),
                              padding: const EdgeInsets.symmetric(vertical: 10),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            ),
                          ),
                        ),
                      ],
                    ],
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildSavedAddressesSection() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.015),
            blurRadius: 12,
            offset: const Offset(0, 6),
          ),
        ],
        border: Border.all(color: const Color(0xFFE5E7EB).withOpacity(0.5), width: 1),
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
                        color: AppTheme.secondaryColor.withOpacity(0.4),
                        shape: BoxShape.circle,
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
                            fontSize: 15.5,
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
          const Divider(height: 1, thickness: 0.5),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: _addresses.isEmpty
                ? const Center(
                    child: Padding(
                      padding: EdgeInsets.symmetric(vertical: 16),
                      child: Text("No addresses saved.", style: TextStyle(color: AppTheme.textColorSecondary, fontStyle: FontStyle.italic)),
                    ),
                  )
                : ListView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: _addresses.length,
                    itemBuilder: (context, index) {
                      final addr = _addresses[index];
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

  Widget _buildAccountSettingsSection() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.015),
            blurRadius: 12,
            offset: const Offset(0, 6),
          ),
        ],
        border: Border.all(color: const Color(0xFFE5E7EB).withOpacity(0.5), width: 1),
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
                    color: AppTheme.secondaryColor.withOpacity(0.4),
                    shape: BoxShape.circle,
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
                        fontSize: 15.5,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.textColorPrimary,
                      ),
                ),
              ],
            ),
          ),
          const Divider(height: 1, thickness: 0.5),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              children: [
                SettingsTile(
                  leadingIcon: Icons.settings_rounded,
                  title: "App Settings",
                  subtitle: "Manage notifications, language, and preferences",
                  onTap: () => Navigator.pushNamed(context, AppRoutes.settings),
                ),
                SettingsTile(
                  leadingIcon: Icons.info_outline_rounded,
                  title: "About App",
                  subtitle: "App version, developers, support and terms",
                  onTap: () => Navigator.pushNamed(context, AppRoutes.aboutApp),
                ),
              ],
            ),
          )
        ],
      ),
    );
  }

  Widget _buildAboutMediLoopSection() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppTheme.cardColor,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFFE5E7EB).withOpacity(0.5), width: 1),
      ),
      child: Column(
        children: [
          Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: AppTheme.secondaryColor.withOpacity(0.4),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: AppTheme.primaryColor.withOpacity(0.2), width: 1.5),
                ),
                child: const Icon(Icons.blur_circular_rounded, color: AppTheme.primaryColor, size: 30),
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
                        color: AppTheme.textColorSecondary,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              )
            ],
          ),
          const SizedBox(height: 14),
          const Text(
            "MediLoop is an AI-powered autonomous pharmacy platform that enables customers to order medicines using voice or text, upload prescriptions, receive intelligent refill reminders, and experience seamless AI-assisted pharmacy services.",
            style: TextStyle(
              fontSize: 12.5,
              height: 1.4,
              color: AppTheme.textColorSecondary,
            ),
          ),
          const Divider(height: 24, thickness: 0.5),
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
              backgroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
              title: const Text("Rate MediLoop", style: TextStyle(fontWeight: FontWeight.bold, color: AppTheme.textColorPrimary), textAlign: TextAlign.center),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text("How has your autonomous pharmacy experience been?", textAlign: TextAlign.center, style: TextStyle(fontSize: 13, color: AppTheme.textColorSecondary)),
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
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text("Cancel", style: TextStyle(color: AppTheme.textColorSecondary, fontWeight: FontWeight.bold)),
                ),
                ElevatedButton(
                  onPressed: () {
                    Navigator.pop(context);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Thank you for rating us $rating stars!')),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.primaryColor,
                    minimumSize: const Size(100, 44),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  child: const Text("Submit"),
                )
              ],
            );
          },
        );
      },
    );
  }

  Widget _buildLogoutButton() {
    return AnimatedButtonWrapper(
      onPressed: _showLogoutDialog,
      child: Container(
        height: 52,
        width: double.infinity,
        decoration: BoxDecoration(
          color: Colors.red.shade700,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.red.shade700.withOpacity(0.2),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        alignment: Alignment.center,
        child: const Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.logout_rounded, size: 20, color: Colors.white),
            SizedBox(width: 8),
            Text(
              "Log Out",
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 15,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
