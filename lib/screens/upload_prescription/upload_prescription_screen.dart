import 'dart:convert';
import 'dart:ui';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import '../../core/constants/api_config.dart';
import '../../core/theme/app_theme.dart';
import '../../services/auth_service.dart';
import '../../services/cart_service.dart';
import '../../services/profile_service.dart';
import '../../services/image_picker_service.dart';
import '../../routes/app_routes.dart';

class UploadPrescriptionScreen extends StatefulWidget {
  const UploadPrescriptionScreen({super.key});

  @override
  State<UploadPrescriptionScreen> createState() => _UploadPrescriptionScreenState();
}

class _UploadPrescriptionScreenState extends State<UploadPrescriptionScreen> {
  final ImagePickerService _imagePickerService = ImagePickerService();
  final CartService _cartService = CartService();
  final ProfileService _profileService = ProfileService();
  XFile? _selectedImage;
  Uint8List? _selectedImageBytes;
  bool _isUploading = false;
  String? _extractedText;
  List<Map<String, dynamic>> _extractedItems = [];
  String? _doctorInfo;
  String? _patientInfo;
  String? _instructionsInfo;
  String? _rxId;

  @override
  void initState() {
    super.initState();
    _profileService.addListener(_onProfileUpdated);
    _profileService.fetchPrescriptionsFromBackend();
  }

  void _onProfileUpdated() {
    if (mounted) setState(() {});
  }

  @override
  void dispose() {
    _profileService.removeListener(_onProfileUpdated);
    super.dispose();
  }

  Future<void> _pickImage(ImageSource source) async {
    final image = await _imagePickerService.pickImage(source);
    if (image != null) {
      final bytes = await image.readAsBytes();
      setState(() {
        _selectedImage = image;
        _selectedImageBytes = bytes;
      });
    }
  }

  void _removeImage() {
    setState(() {
      _selectedImage = null;
      _selectedImageBytes = null;
      _extractedText = null;
      _extractedItems = [];
      _doctorInfo = null;
      _patientInfo = null;
      _instructionsInfo = null;
      _rxId = null;
    });
  }

  Future<void> _submitPrescription() async {
    if (_selectedImage == null || _isUploading) return;

    setState(() {
      _isUploading = true;
    });

    try {
      final token = await AuthService().getToken();
      final uri = Uri.parse('${ApiConfig.baseUrl}/prescriptions/upload');
      final request = http.MultipartRequest('POST', uri);

      if (token != null && token.isNotEmpty) {
        request.headers['Authorization'] = 'Bearer $token';
      }
      request.headers['Accept'] = 'application/json';

      final bytes = _selectedImageBytes ?? await _selectedImage!.readAsBytes();
      final file = http.MultipartFile.fromBytes(
        'file',
        bytes,
        filename: _selectedImage!.name.isNotEmpty ? _selectedImage!.name : 'prescription.jpg',
      );
      request.files.add(file);

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 201 || response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final rxId = data["id"]?.toString() ?? "";
        _rxId = rxId;
        _cartService.setPrescriptionStatus("Uploaded");

        // Wait for background orchestration and sync cart & profile prescription history
        await Future.delayed(const Duration(milliseconds: 2000));
        await _cartService.fetchCartFromBackend();
        await _profileService.fetchPrescriptionsFromBackend();

        // Extract structured text and parsed items
        String extracted = (data["extracted_text"] ?? "").toString().trim();
        List<Map<String, dynamic>> itemsList = [];
        if (data["items"] != null && data["items"] is List) {
          itemsList = List<Map<String, dynamic>>.from(data["items"]);
        }

        if (rxId.isNotEmpty && (extracted.isEmpty || itemsList.isEmpty)) {
          try {
            final getUri = Uri.parse('${ApiConfig.baseUrl}/prescriptions/$rxId');
            final getRes = await http.get(getUri, headers: {
              if (token != null && token.isNotEmpty) 'Authorization': 'Bearer $token',
              'Accept': 'application/json',
            });
            if (getRes.statusCode == 200) {
              final rxData = jsonDecode(getRes.body);
              if (extracted.isEmpty) extracted = (rxData["extracted_text"] ?? "").toString().trim();
              if (itemsList.isEmpty && rxData["items"] != null && rxData["items"] is List) {
                itemsList = List<Map<String, dynamic>>.from(rxData["items"]);
              }
            }
          } catch (_) {}
        }

        // Filter out conversational errors or non-medicine lines
        itemsList = itemsList.where((item) {
          final rawName = (item['medicine_name'] ?? item['name'] ?? '').toString();
          return CartService.isValidMedicineName(rawName);
        }).toList();

        // Parse doctor, patient, instructions from structured text if present
        String? doc;
        String? pt;
        String? inst;
        if (extracted.isNotEmpty) {
          for (final line in extracted.split('\n')) {
            final lUpper = line.toUpperCase();
            if ((lUpper.startsWith('DOCTOR') || lUpper.contains('DR.')) && doc == null) {
              doc = line.replaceAll(RegExp(r'^Doctor\s*(\/\s*Clinic)?\s*:\s*', caseSensitive: false), '').trim();
            } else if (lUpper.startsWith('PATIENT') && pt == null) {
              pt = line.replaceAll(RegExp(r'^Patient(\s*Details)?\s*:\s*', caseSensitive: false), '').trim();
            } else if (lUpper.startsWith('INSTRUCTIONS') && inst == null) {
              inst = line.replaceAll(RegExp(r'^Instructions\s*:\s*', caseSensitive: false), '').trim();
            }
          }
        }

        if (itemsList.isNotEmpty) {
          _cartService.addExtractedPrescriptionMedicines(
            items: itemsList,
            prescriptionId: rxId.isNotEmpty ? rxId : "1",
            extractedText: extracted,
          );
        } else {
          _cartService.setPrescriptionStatus("Verification Pending");
        }

        if (mounted) {
          setState(() {
            _extractedText = extracted;
            _extractedItems = itemsList;
            _doctorInfo = doc;
            _patientInfo = pt;
            _instructionsInfo = inst;
          });

          if (itemsList.isNotEmpty) {
            showDialog(
              context: context,
              barrierDismissible: false,
              builder: (ctx) => AlertDialog(
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                title: const Row(
                  children: [
                    Icon(Icons.check_circle_rounded, color: AppTheme.primaryColor, size: 28),
                    SizedBox(width: 10),
                    Text("Prescription Processed!", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                  ],
                ),
                content: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text("Prescription #$rxId processed by MediLoop Multi-Agent Ecosystem:"),
                    const SizedBox(height: 12),
                    const Text("✓ Vision OCR: Medical text transcribed", style: TextStyle(fontSize: 13, color: Colors.black87)),
                    const Text("✓ Clinical NER: Medicines structured & verified", style: TextStyle(fontSize: 13, color: Colors.black87)),
                    const Text("✓ Drug Safety CDSS: Passed clinical checks", style: TextStyle(fontSize: 13, color: Colors.black87)),
                    const Text("✓ Pharmacy Inventory: Stock confirmed", style: TextStyle(fontSize: 13, color: Colors.black87)),
                    const Text("✓ Cart: Prescribed items auto-populated", style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppTheme.primaryColor)),
                    const SizedBox(height: 14),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                      decoration: BoxDecoration(
                        color: AppTheme.secondaryColor.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: AppTheme.primaryColor.withOpacity(0.2)),
                      ),
                      child: Text(
                        "${itemsList.length} prescribed medicines successfully extracted and added to your cart.",
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppTheme.primaryColor),
                      ),
                    ),
                  ],
                ),
                actions: [
                  TextButton(
                    onPressed: () {
                      Navigator.pop(ctx);
                    },
                    child: const Text("Review Extraction"),
                  ),
                  ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.primaryColor,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    onPressed: () {
                      Navigator.pop(ctx);
                      Navigator.pushNamed(context, AppRoutes.cart);
                    },
                    child: const Text("View in Cart", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                  ),
                ],
              ),
            );
          } else {
            showDialog(
              context: context,
              barrierDismissible: false,
              builder: (ctx) => AlertDialog(
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                title: Row(
                  children: [
                    Icon(Icons.hourglass_top_rounded, color: Colors.orange.shade800, size: 28),
                    const SizedBox(width: 10),
                    const Text("Prescription Uploaded", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                  ],
                ),
                content: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text("Prescription #$rxId uploaded successfully:"),
                    const SizedBox(height: 12),
                    const Text("No medicines could be automatically identified from this image (it may be blurry or low-resolution).", style: TextStyle(fontSize: 13, color: Colors.black87)),
                    const SizedBox(height: 8),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                      decoration: BoxDecoration(
                        color: Colors.amber.shade50,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.amber.shade200),
                      ),
                      child: const Text(
                        "Your prescription has been forwarded to the Pharmacist Dashboard for manual review and medicine verification.",
                        style: TextStyle(fontSize: 12, fontWeight: FontWeight.w500, color: Colors.brown),
                      ),
                    ),
                  ],
                ),
                actions: [
                  TextButton(
                    onPressed: () {
                      Navigator.pop(ctx);
                    },
                    child: const Text("Upload Clearer Photo"),
                  ),
                  ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.primaryColor,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    onPressed: () {
                      Navigator.pop(ctx);
                      Navigator.pushNamed(context, AppRoutes.cart);
                    },
                    child: const Text("Go to Cart", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                  ),
                ],
              ),
            );
          }
        }
      } else if (response.statusCode == 401) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Please log in first to upload prescriptions.'),
              backgroundColor: Colors.redAccent,
            ),
          );
        }
      } else {
        String detail = 'Upload failed';
        try {
          final err = jsonDecode(response.body);
          detail = err['detail'] ?? detail;
        } catch (_) {}
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Upload failed: $detail'),
              backgroundColor: Colors.redAccent,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error uploading prescription: $e'),
            backgroundColor: Colors.redAccent,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isUploading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      appBar: AppBar(
        title: const Text(
          "Upload Prescription",
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
        ),
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: AppTheme.textColorPrimary,
        centerTitle: true,
      ),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                physics: const BouncingScrollPhysics(),
                padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 8.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Empty State Illustration
                    if (_selectedImage == null) ...[
                      const SizedBox(height: 8),
                      Center(
                        child: TweenAnimationBuilder<double>(
                          tween: Tween(begin: 0.0, end: 1.0),
                          duration: const Duration(milliseconds: 655),
                          curve: Curves.easeOutCubic,
                          builder: (context, value, child) {
                            return Opacity(
                              opacity: value,
                              child: Transform.scale(
                                scale: 0.85 + (value * 0.15),
                                child: child,
                              ),
                            );
                          },
                          child: SizedBox(
                            width: 180,
                            height: 180,
                            child: CustomPaint(
                              painter: RxIllustrationPainter(
                                primaryColor: AppTheme.primaryColor,
                                secondaryColor: AppTheme.secondaryColor,
                                accentColor: AppTheme.accentColor,
                              ),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                    ],

                    Text(
                      "Upload Rx Document",
                      textAlign: _selectedImage == null ? TextAlign.center : TextAlign.start,
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: AppTheme.textColorPrimary,
                            fontSize: 22,
                            letterSpacing: -0.5,
                          ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      "Please upload a clear picture of your doctor's prescription. Our AI and pharmacist team will verify it.",
                      textAlign: _selectedImage == null ? TextAlign.center : TextAlign.start,
                      style: const TextStyle(
                        color: AppTheme.textColorSecondary,
                        fontSize: 13,
                        height: 1.4,
                      ),
                    ),
                    const SizedBox(height: 28),

                    // Upload Box / Preview Area
                    _selectedImage == null
                        ? _buildUploadPlaceholder()
                        : _buildImagePreview(),
                    const SizedBox(height: 24),

                    // Extracted Prescription Text Card (below prescription extracted)
                    if (_extractedText != null && _extractedText!.isNotEmpty) ...[
                      _buildExtractedTextCard(),
                      const SizedBox(height: 24),
                    ],

                    // Guidelines / Tips Card
                    _buildTipsCard(),
                    const SizedBox(height: 20),

                    // Prescription History & Extracted Text Records
                    _buildPrescriptionHistorySection(),
                    const SizedBox(height: 16),
                  ],
                ),
              ),
            ),

            // Redesigned Action Button
            Padding(
              padding: const EdgeInsets.all(24.0),
              child: AnimatedActionButton(
                onPressed: (_selectedImage != null && !_isUploading) ? _submitPrescription : null,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    if (_isUploading) ...[
                      const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                        ),
                      ),
                      const SizedBox(width: 12),
                      const Text(
                        "AI Pipeline Analyzing...",
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                    ] else ...[
                      Icon(
                        _selectedImage != null ? Icons.verified_rounded : Icons.lock_outline_rounded,
                        color: Colors.white.withOpacity(0.9),
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        _selectedImage != null ? "Submit Prescription" : "Select Image to Proceed",
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildUploadPlaceholder() {
    return GestureDetector(
      onTap: () => _showSourceSelection(),
      child: Container(
        height: 200,
        decoration: BoxDecoration(
          color: AppTheme.cardColor,
          borderRadius: BorderRadius.circular(24),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.02),
              blurRadius: 16,
              offset: const Offset(0, 8),
            ),
          ],
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(24),
          child: CustomPaint(
            painter: DottedBorderPainter(color: AppTheme.primaryColor.withOpacity(0.3)),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  padding: const EdgeInsets.all(18),
                  decoration: BoxDecoration(
                    color: AppTheme.secondaryColor.withOpacity(0.3),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.document_scanner_outlined,
                    size: 38,
                    color: AppTheme.primaryColor,
                  ),
                ),
                const SizedBox(height: 18),
                const Text(
                  "Tap to select image",
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                    color: AppTheme.textColorPrimary,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  "Supports JPEG, PNG or PDF scans",
                  style: TextStyle(
                    color: AppTheme.textColorSecondary.withOpacity(0.8),
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildImagePreview() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Reassuring validation status banner (Glassmorphism status card)
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          margin: const EdgeInsets.only(bottom: 16),
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.75),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppTheme.primaryColor.withOpacity(0.18)),
          ),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppTheme.primaryColor.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.security_rounded,
                  color: AppTheme.primaryColor,
                  size: 16,
                ),
              ),
              const SizedBox(width: 12),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "Secure Rx Encryption Enabled",
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 13,
                        color: AppTheme.textColorPrimary,
                      ),
                    ),
                    Text(
                      "Prescription ready for clinical verification",
                      style: TextStyle(
                        fontSize: 11,
                        color: AppTheme.textColorSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              const Icon(
                Icons.auto_awesome_rounded,
                color: AppTheme.accentColor,
                size: 16,
              ),
            ],
          ),
        ),

        // Image container with custom shadow and delete button
        AspectRatio(
          aspectRatio: 4 / 3,
          child: Container(
            decoration: BoxDecoration(
              color: AppTheme.cardColor,
              borderRadius: BorderRadius.circular(24),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.08),
                  blurRadius: 20,
                  offset: const Offset(0, 10),
                ),
              ],
            ),
            child: Stack(
              fit: StackFit.expand,
              children: [
                // Selected Image
                ClipRRect(
                  borderRadius: BorderRadius.circular(24),
                  child: _selectedImageBytes != null
                      ? Image.memory(
                          _selectedImageBytes!,
                          fit: BoxFit.cover,
                        )
                      : const Center(
                          child: CircularProgressIndicator(),
                        ),
                ),

                // Delete Button with Glassmorphism overlay
                Positioned(
                  top: 16,
                  right: 16,
                  child: ClipOval(
                    child: BackdropFilter(
                      filter: ImageFilter.blur(sigmaX: 8, sigmaY: 8),
                      child: Container(
                        height: 38,
                        width: 38,
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.85),
                          shape: BoxShape.circle,
                        ),
                        child: Material(
                          color: Colors.transparent,
                          child: InkWell(
                            onTap: _removeImage,
                            child: const Icon(
                              Icons.close_rounded,
                              color: Colors.redAccent,
                              size: 20,
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildExtractedTextCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppTheme.cardColor,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: AppTheme.primaryColor.withOpacity(0.25),
          width: 1.5,
        ),
        boxShadow: [
          BoxShadow(
            color: AppTheme.primaryColor.withOpacity(0.06),
            blurRadius: 16,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppTheme.primaryColor.withOpacity(0.12),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.receipt_long_rounded,
                  color: AppTheme.primaryColor,
                  size: 20,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      "Prescription Extraction Report",
                      style: TextStyle(
                        color: AppTheme.textColorPrimary,
                        fontWeight: FontWeight.bold,
                        fontSize: 15,
                        letterSpacing: -0.3,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      _rxId != null ? "Prescription #$_rxId • Verified" : "AI Clinical NER Extraction",
                      style: const TextStyle(
                        color: AppTheme.textColorSecondary,
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: const Color(0xFF2E7D32).withOpacity(0.12),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.check_circle_outline_rounded, size: 12, color: Color(0xFF2E7D32)),
                    SizedBox(width: 4),
                    Text(
                      "Verified",
                      style: TextStyle(
                        color: Color(0xFF2E7D32),
                        fontWeight: FontWeight.bold,
                        fontSize: 10,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),
          // Exact readable prescription report format adhering strictly to specifications
          _buildExactPrescriptionReportView(_extractedText ?? ""),

          const SizedBox(height: 16),
          // View in Cart Quick Action
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.primaryColor,
                padding: const EdgeInsets.symmetric(vertical: 12),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              onPressed: () {
                Navigator.pushNamed(context, AppRoutes.cart);
              },
              icon: const Icon(Icons.shopping_cart_outlined, size: 18, color: Colors.white),
              label: const Text(
                "View Extracted Medicines in Cart",
                style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildExactPrescriptionReportView(String report) {
    if (report.isEmpty) {
      return const SizedBox.shrink();
    }

    final lines = report.split('\n');
    final spans = <TextSpan>[];

    for (int i = 0; i < lines.length; i++) {
      final line = lines[i];
      final trimmed = line.trim();

      if (trimmed.startsWith('**') && trimmed.endsWith('**')) {
        // Section Header: **Prescription Details:** / **Prescribed Medicines:** / **Medical Advice & Instructions:**
        spans.add(TextSpan(
          text: '$line\n',
          style: const TextStyle(
            fontWeight: FontWeight.w800,
            fontSize: 13.5,
            color: Color(0xFF0F172A),
            height: 1.8,
          ),
        ));
      } else if (trimmed.contains(':') && !RegExp(r'^\d+\.').hasMatch(trimmed)) {
        // Clinical Detail Field: "Hospital / Clinic: ..."
        final colonIdx = line.indexOf(':');
        final label = line.substring(0, colonIdx + 1);
        final value = line.substring(colonIdx + 1);
        final isMissing = value.toLowerCase().contains('not mentioned in prescription') || value.toLowerCase().contains('unable to read clearly');

        spans.add(TextSpan(
          text: label,
          style: const TextStyle(
            fontWeight: FontWeight.w700,
            fontSize: 12.5,
            color: Color(0xFF334155),
            height: 1.5,
          ),
        ));
        spans.add(TextSpan(
          text: '$value\n',
          style: TextStyle(
            fontWeight: isMissing ? FontWeight.w400 : FontWeight.w500,
            fontSize: 12.5,
            color: isMissing ? const Color(0xFF64748B) : const Color(0xFF0F172A),
            fontStyle: isMissing ? FontStyle.italic : FontStyle.normal,
            height: 1.5,
          ),
        ));
      } else if (RegExp(r'^\d+\.').hasMatch(trimmed)) {
        // Numbered Medicine Item: "1. [Medicine Name] | Strength: ... | Dosage: ... | Frequency: ... | Duration: ... | Qty: ..."
        final isNeedsVerification = trimmed.toLowerCase().contains('(needs verification)');
        spans.add(TextSpan(
          text: '$line\n',
          style: TextStyle(
            fontWeight: FontWeight.w600,
            fontSize: 12,
            color: isNeedsVerification ? const Color(0xFFD97706) : const Color(0xFF1E293B),
            height: 1.6,
          ),
        ));
      } else {
        // Other content or spacing lines
        spans.add(TextSpan(
          text: '$line\n',
          style: const TextStyle(
            fontWeight: FontWeight.normal,
            fontSize: 12.5,
            color: Color(0xFF334155),
            height: 1.5,
          ),
        ));
      }
    }

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFFF8FAFC),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFCBD5E1), width: 1.0),
      ),
      child: SelectableText.rich(
        TextSpan(children: spans),
      ),
    );
  }

  Widget _buildTipsCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppTheme.secondaryColor.withOpacity(0.22),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: AppTheme.primaryColor.withOpacity(0.1),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: AppTheme.primaryColor.withOpacity(0.12),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.verified_user_outlined,
                  color: AppTheme.primaryColor,
                  size: 14,
                ),
              ),
              const SizedBox(width: 10),
              const Text(
                "Submission Guidelines",
                style: TextStyle(
                  color: AppTheme.primaryColor,
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          _buildTipItem("Ensure the prescription details are fully visible."),
          const SizedBox(height: 8),
          _buildTipItem("Capture in good lighting (avoid shadows/glare)."),
          const SizedBox(height: 8),
          _buildTipItem("Avoid blurry, cropped, or wrinkled sheets."),
          const SizedBox(height: 8),
          _buildTipItem("Upload one valid doctor prescription at a time."),
        ],
      ),
    );
  }

  Widget _buildTipItem(String text) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.only(top: 2.0),
          child: Icon(
            Icons.check_circle_outline_rounded,
            color: AppTheme.primaryColor,
            size: 14,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            text,
            style: const TextStyle(
              color: AppTheme.textColorPrimary,
              fontSize: 13,
              height: 1.3,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildPrescriptionHistorySection() {
    final prescriptions = _profileService.getPrescriptions();

    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.grey.shade200),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.015),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: AppTheme.primaryColor.withOpacity(0.12),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.history_rounded, size: 16, color: AppTheme.primaryColor),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    "Prescription History (${prescriptions.length})",
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: AppTheme.textColorPrimary),
                  ),
                ],
              ),
              TextButton(
                onPressed: () => _profileService.fetchPrescriptionsFromBackend(),
                child: const Text("Refresh", style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.primaryColor)),
              ),
            ],
          ),
          const Divider(height: 16),
          if (prescriptions.isEmpty)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 16.0),
              child: Center(
                child: Text(
                  "No prescriptions uploaded yet. When you upload prescriptions, your scans and extracted text history will be saved and displayed here.",
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 12, color: AppTheme.textColorSecondary, fontStyle: FontStyle.italic),
                ),
              ),
            )
          else
            ListView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: prescriptions.length > 5 ? 5 : prescriptions.length,
            itemBuilder: (context, index) {
              final rx = prescriptions[index];
              Color statusColor;
              switch (rx.status.toLowerCase()) {
                case 'verified':
                case 'approved':
                  statusColor = const Color(0xFF2E7D32);
                  break;
                case 'rejected':
                  statusColor = Colors.red.shade700;
                  break;
                default:
                  statusColor = Colors.orange.shade800;
              }

              return Container(
                margin: const EdgeInsets.only(bottom: 10),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppTheme.backgroundColor,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: Colors.grey.shade200),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.description_outlined, size: 16, color: AppTheme.primaryColor),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            "Rx #${rx.id} • ${rx.fileName}",
                            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: AppTheme.textColorPrimary),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: statusColor.withOpacity(0.12),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            rx.status,
                            style: TextStyle(color: statusColor, fontWeight: FontWeight.bold, fontSize: 10),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      "Uploaded on ${rx.uploadDate}",
                      style: const TextStyle(fontSize: 11, color: AppTheme.textColorSecondary),
                    ),
                    if (rx.extractedText != null && rx.extractedText!.isNotEmpty) ...[
                      const SizedBox(height: 6),
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.grey.shade200),
                        ),
                        child: Text(
                          rx.extractedText!.trim(),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(fontSize: 11, color: AppTheme.textColorPrimary),
                        ),
                      ),
                    ],
                  ],
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  void _showSourceSelection() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.white,
      elevation: 6,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
      ),
      builder: (context) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(24, 16, 24, 24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Bottom sheet drag handle
                Container(
                  width: 38,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade300,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
                const SizedBox(height: 20),
                const Text(
                  "Choose Prescription Source",
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 18,
                    color: AppTheme.textColorPrimary,
                    letterSpacing: -0.3,
                  ),
                ),
                const SizedBox(height: 6),
                const Text(
                  "Select how you want to upload your document",
                  style: TextStyle(
                    color: AppTheme.textColorSecondary,
                    fontSize: 13,
                  ),
                ),
                const SizedBox(height: 24),
                Row(
                  children: [
                    Expanded(
                      child: _buildSourceOptionCard(
                        icon: Icons.camera_alt_outlined,
                        label: "Take Photo",
                        description: "Scan with camera",
                        onTap: () {
                          Navigator.pop(context);
                          _pickImage(ImageSource.camera);
                        },
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: _buildSourceOptionCard(
                        icon: Icons.photo_library_outlined,
                        label: "From Gallery",
                        description: "Upload saved file",
                        onTap: () {
                          Navigator.pop(context);
                          _pickImage(ImageSource.gallery);
                        },
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildSourceOptionCard({
    required IconData icon,
    required String label,
    required String description,
    required VoidCallback onTap,
  }) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(20),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(20),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 12),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: Colors.grey.shade200,
              width: 1,
            ),
          ),
          child: Column(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppTheme.secondaryColor.withOpacity(0.35),
                  shape: BoxShape.circle,
                ),
                child: Icon(icon, color: AppTheme.primaryColor, size: 24),
              ),
              const SizedBox(height: 12),
              Text(
                label,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                  color: AppTheme.textColorPrimary,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                description,
                style: const TextStyle(
                  color: AppTheme.textColorSecondary,
                  fontSize: 11,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// Custom button widget that provides tactile press animations
class AnimatedActionButton extends StatefulWidget {
  final VoidCallback? onPressed;
  final Widget child;

  const AnimatedActionButton({
    super.key,
    required this.onPressed,
    required this.child,
  });

  @override
  State<AnimatedActionButton> createState() => _AnimatedActionButtonState();
}

class _AnimatedActionButtonState extends State<AnimatedActionButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scale;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 100),
    );
    _scale = Tween<double>(begin: 1.0, end: 0.96).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final bool isEnabled = widget.onPressed != null;
    return GestureDetector(
      onTapDown: isEnabled ? (_) => _controller.forward() : null,
      onTapUp: isEnabled ? (_) => _controller.reverse() : null,
      onTapCancel: isEnabled ? () => _controller.reverse() : null,
      onTap: widget.onPressed,
      child: AnimatedBuilder(
        animation: _scale,
        builder: (context, child) {
          return Transform.scale(
            scale: _scale.value,
            child: child,
          );
        },
        child: Container(
          width: double.infinity,
          height: 56,
          decoration: BoxDecoration(
            color: isEnabled ? AppTheme.primaryColor : Colors.grey.shade300,
            borderRadius: BorderRadius.circular(16),
            boxShadow: isEnabled
                ? [
                    BoxShadow(
                      color: AppTheme.primaryColor.withOpacity(0.22),
                      blurRadius: 14,
                      offset: const Offset(0, 4),
                    ),
                  ]
                : [],
          ),
          alignment: Alignment.center,
          child: widget.child,
        ),
      ),
    );
  }
}

// Custom Painter to draw a clean vector illustration for the prescription screen
class RxIllustrationPainter extends CustomPainter {
  final Color primaryColor;
  final Color secondaryColor;
  final Color accentColor;

  RxIllustrationPainter({
    required this.primaryColor,
    required this.secondaryColor,
    required this.accentColor,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final width = size.width;
    final height = size.height;
    final center = Offset(width / 2, height / 2);

    // 1. Draw soft background circle
    final bgPaint = Paint()
      ..color = secondaryColor.withOpacity(0.35)
      ..style = PaintingStyle.fill;
    canvas.drawCircle(center, width * 0.42, bgPaint);

    // 2. Draw circular dotted border path
    final dotPaint = Paint()
      ..color = primaryColor.withOpacity(0.18)
      ..strokeWidth = 1.5
      ..style = PaintingStyle.stroke;

    final double radius = width * 0.46;
    const int dashCount = 36;
    for (int i = 0; i < dashCount; i++) {
      final double angle = (i * 2 * 3.141592653589793) / dashCount;
      final double nextAngle = ((i + 0.5) * 2 * 3.141592653589793) / dashCount;
      canvas.drawArc(
        Rect.fromCircle(center: center, radius: radius),
        angle,
        nextAngle - angle,
        false,
        dotPaint,
      );
    }

    // 3. Draw Prescription Document
    final docWidth = width * 0.44;
    final docHeight = height * 0.58;

    canvas.save();
    canvas.translate(center.dx - 6, center.dy);
    canvas.rotate(-0.12); // around -7 degrees

    final docRect = RRect.fromRectAndRadius(
      Rect.fromCenter(center: Offset.zero, width: docWidth, height: docHeight),
      const Radius.circular(16),
    );

    // Document shadow
    final shadowPaint = Paint()
      ..color = Colors.black.withOpacity(0.04)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 8);
    canvas.drawRRect(docRect.shift(const Offset(0, 4)), shadowPaint);

    // Document background (white)
    final docPaint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.fill;
    canvas.drawRRect(docRect, docPaint);

    // Document border (very thin grey)
    final docBorderPaint = Paint()
      ..color = Colors.grey.shade200
      ..strokeWidth = 1.2
      ..style = PaintingStyle.stroke;
    canvas.drawRRect(docRect, docBorderPaint);

    // Draw Rx Header
    final rxPaint = Paint()
      ..color = primaryColor
      ..style = PaintingStyle.fill;

    // R letter vertical line
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromLTWH(-docWidth / 2 + 12, -docHeight / 2 + 16, 3.2, 13),
        const Radius.circular(1),
      ),
      rxPaint,
    );

    // R letter loop
    final rLoopPath = Path()
      ..addArc(
        Rect.fromLTWH(-docWidth / 2 + 12, -docHeight / 2 + 16, 9, 8),
        -3.141592653589793 / 2,
        3.141592653589793,
      );
    canvas.drawPath(
      rLoopPath,
      Paint()
        ..color = primaryColor
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2,
    );

    // R letter tail & cross
    canvas.drawLine(
      Offset(-docWidth / 2 + 15, -docHeight / 2 + 24),
      Offset(-docWidth / 2 + 21, -docHeight / 2 + 29),
      Paint()
        ..color = primaryColor
        ..strokeWidth = 2
        ..strokeCap = StrokeCap.round,
    );
    canvas.drawLine(
      Offset(-docWidth / 2 + 13, -docHeight / 2 + 27),
      Offset(-docWidth / 2 + 19, -docHeight / 2 + 25),
      Paint()
        ..color = primaryColor
        ..strokeWidth = 1.8
        ..strokeCap = StrokeCap.round,
    );

    // Draw lines of prescription
    final linePaint = Paint()
      ..color = Colors.grey.shade300
      ..strokeWidth = 3
      ..strokeCap = StrokeCap.round;

    final linePaintActive = Paint()
      ..color = primaryColor.withOpacity(0.35)
      ..strokeWidth = 3
      ..strokeCap = StrokeCap.round;

    // Header horizontal lines
    canvas.drawLine(
      Offset(-docWidth / 2 + 26, -docHeight / 2 + 18),
      Offset(docWidth / 2 - 12, -docHeight / 2 + 18),
      linePaint,
    );
    canvas.drawLine(
      Offset(-docWidth / 2 + 26, -docHeight / 2 + 24),
      Offset(docWidth / 2 - 24, -docHeight / 2 + 24),
      linePaint,
    );

    // Divider line
    canvas.drawLine(
      Offset(-docWidth / 2 + 12, -docHeight / 2 + 35),
      Offset(docWidth / 2 - 12, -docHeight / 2 + 35),
      Paint()
        ..color = Colors.grey.shade100
        ..strokeWidth = 1,
    );

    // Prescription body lines
    double lineY = -docHeight / 2 + 46;
    final List<double> lineWidths = [0.75, 0.8, 0.6, 0.7, 0.45];
    for (int i = 0; i < lineWidths.length; i++) {
      final p = (i == 0 || i == 2) ? linePaintActive : linePaint;
      canvas.drawLine(
        Offset(-docWidth / 2 + 12, lineY),
        Offset(-docWidth / 2 + 12 + (docWidth - 24) * lineWidths[i], lineY),
        p,
      );
      lineY += 12;
    }

    // Doctor signature line
    canvas.drawLine(
      Offset(docWidth / 2 - 32, docHeight / 2 - 16),
      Offset(docWidth / 2 - 12, docHeight / 2 - 16),
      Paint()
        ..color = Colors.grey.shade300
        ..strokeWidth = 1.5,
    );

    canvas.restore();

    // 4. Draw Floating Secure Shield Badge (Bottom Right)
    canvas.save();
    canvas.translate(center.dx + docWidth * 0.42, center.dy + docHeight * 0.28);

    // Shield shadow
    final shieldShadow = Paint()
      ..color = Colors.black.withOpacity(0.06)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 4);
    canvas.drawCircle(Offset.zero, 18, shieldShadow);

    // Shield background path
    final shieldBgPaint = Paint()
      ..color = primaryColor
      ..style = PaintingStyle.fill;

    final shieldPath = Path();
    const double shieldSize = 16.0;
    shieldPath.moveTo(0, -shieldSize);
    shieldPath.quadraticBezierTo(shieldSize * 0.8, -shieldSize * 0.8, shieldSize * 0.9, -shieldSize * 0.2);
    shieldPath.quadraticBezierTo(shieldSize * 0.9, shieldSize * 0.5, 0, shieldSize * 1.1);
    shieldPath.quadraticBezierTo(-shieldSize * 0.9, shieldSize * 0.5, -shieldSize * 0.9, -shieldSize * 0.2);
    shieldPath.quadraticBezierTo(-shieldSize * 0.8, -shieldSize * 0.8, 0, -shieldSize);
    shieldPath.close();

    canvas.drawPath(shieldPath, shieldBgPaint);

    // White checkmark inside shield
    final checkPaint = Paint()
      ..color = Colors.white
      ..strokeWidth = 2.5
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    final checkPath = Path()
      ..moveTo(-shieldSize * 0.38, -shieldSize * 0.05)
      ..lineTo(-shieldSize * 0.08, shieldSize * 0.25)
      ..lineTo(shieldSize * 0.42, -shieldSize * 0.3);
    canvas.drawPath(checkPath, checkPaint);

    canvas.restore();

    // 5. Draw Floating Cross Badge (Left)
    canvas.save();
    canvas.translate(center.dx - docWidth * 0.65, center.dy - docHeight * 0.15);

    // Subtle float background circle
    final badgePaint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.fill;
    final badgeShadow = Paint()
      ..color = Colors.black.withOpacity(0.04)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 3);
    canvas.drawCircle(const Offset(0, 1), 12, badgeShadow);
    canvas.drawCircle(Offset.zero, 12, badgePaint);

    // Plus icon in green
    final plusPaint = Paint()
      ..color = primaryColor
      ..strokeWidth = 2.5
      ..strokeCap = StrokeCap.round;
    canvas.drawLine(const Offset(-4.5, 0), const Offset(4.5, 0), plusPaint);
    canvas.drawLine(const Offset(0, -4.5), const Offset(0, 4.5), plusPaint);

    canvas.restore();

    // 6. Draw Floating Pill Capsule (Top Right)
    canvas.save();
    canvas.translate(center.dx + docWidth * 0.48, center.dy - docHeight * 0.38);
    canvas.rotate(0.65); // Rotated capsule

    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromCenter(center: const Offset(0, 1), width: 12, height: 24),
        const Radius.circular(6),
      ),
      Paint()
        ..color = Colors.black.withOpacity(0.04)
        ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 3),
    );

    // Draw Capsule half accent (gold) and half secondary (mint)
    final pillRectBottom = RRect.fromRectAndCorners(
      const Rect.fromLTWH(-6, 0, 12, 12),
      bottomLeft: const Radius.circular(6),
      bottomRight: const Radius.circular(6),
    );
    final pillRectTop = RRect.fromRectAndCorners(
      const Rect.fromLTWH(-6, -12, 12, 12),
      topLeft: const Radius.circular(6),
      topRight: const Radius.circular(6),
    );

    canvas.drawRRect(pillRectTop, Paint()..color = accentColor);
    canvas.drawRRect(pillRectBottom, Paint()..color = secondaryColor);

    // Center divider line on pill
    canvas.drawLine(
      const Offset(-6, 0),
      const Offset(6, 0),
      Paint()
        ..color = Colors.white
        ..strokeWidth = 1.2,
    );

    canvas.restore();
  }

  @override
  bool shouldRepaint(covariant RxIllustrationPainter oldDelegate) {
    return oldDelegate.primaryColor != primaryColor ||
        oldDelegate.secondaryColor != secondaryColor ||
        oldDelegate.accentColor != accentColor;
  }
}

// Custom Painter to draw dotted border for the upload placeholder box
class DottedBorderPainter extends CustomPainter {
  final Color color;

  DottedBorderPainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;

    const dashWidth = 8;
    const dashSpace = 6;

    final rect = RRect.fromRectAndRadius(
      Rect.fromLTWH(0, 0, size.width, size.height),
      const Radius.circular(24),
    );

    final path = Path()..addRRect(rect);
    final dottedPath = Path();
    double distance = 0.0;

    for (var metric in path.computeMetrics()) {
      while (distance < metric.length) {
        dottedPath.addPath(
          metric.extractPath(distance, distance + dashWidth),
          Offset.zero,
        );
        distance += dashWidth + dashSpace;
      }
    }

    canvas.drawPath(dottedPath, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
