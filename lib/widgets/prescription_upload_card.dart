import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import '../services/cart_service.dart';
import '../routes/app_routes.dart';

class PrescriptionUploadCard extends StatefulWidget {
  const PrescriptionUploadCard({super.key});

  @override
  State<PrescriptionUploadCard> createState() => _PrescriptionUploadCardState();
}

class _PrescriptionUploadCardState extends State<PrescriptionUploadCard> {
  final CartService _cartService = CartService();

  @override
  void initState() {
    super.initState();
    _cartService.addListener(_onCartChanged);
  }

  @override
  void dispose() {
    _cartService.removeListener(_onCartChanged);
    super.dispose();
  }

  void _onCartChanged() {
    if (mounted) {
      setState(() {});
    }
  }

  @override
  Widget build(BuildContext context) {
    final status = _cartService.prescriptionStatus;
    final isUploaded = status != "None";

    Color statusColor = Colors.grey;
    IconData statusIcon = Icons.description_outlined;
    String statusLabel = "No Prescription Uploaded";

    if (status == "Uploaded") {
      statusColor = Colors.blue.shade800;
      statusIcon = Icons.cloud_done_outlined;
      statusLabel = "Prescription Uploaded";
    } else if (status == "Verification Pending") {
      statusColor = Colors.orange.shade800;
      statusIcon = Icons.hourglass_empty_rounded;
      statusLabel = "Pending Verification";
    } else if (status == "Verified") {
      statusColor = AppTheme.primaryColor;
      statusIcon = Icons.verified_rounded;
      statusLabel = "Verified by AI Pharmacist";
    }

    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: AppTheme.cardColor,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(
          color: const Color(0xFFE5E7EB).withOpacity(0.5),
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 16,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    "Upload Prescription",
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: AppTheme.textColorPrimary,
                      letterSpacing: -0.3,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    isUploaded 
                        ? "Prescription status: $statusLabel"
                        : "Upload your doctor's prescription for prescription medicines.",
                    style: TextStyle(
                      fontSize: 13,
                      color: isUploaded ? statusColor : AppTheme.textColorSecondary,
                      fontWeight: isUploaded ? FontWeight.w700 : FontWeight.normal,
                      height: 1.4,
                    ),
                  ),
                  const SizedBox(height: 18),
                  ElevatedButton.icon(
                    onPressed: () {
                      Navigator.pushNamed(context, AppRoutes.uploadPrescription);
                    },
                    icon: Icon(
                      isUploaded ? Icons.edit_document : Icons.cloud_upload_outlined, 
                      size: 18,
                    ),
                    label: Text(
                      isUploaded ? "Manage" : "Upload Image",
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: isUploaded ? statusColor : AppTheme.primaryColor,
                      foregroundColor: Colors.white,
                      elevation: 0,
                      minimumSize: const Size(140, 46),
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(14),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 16),
            Stack(
              clipBehavior: Clip.none,
              children: [
                Container(
                  width: 88,
                  height: 88,
                  decoration: BoxDecoration(
                    color: isUploaded ? statusColor.withOpacity(0.06) : AppTheme.primaryColor.withOpacity(0.05),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: isUploaded ? statusColor.withOpacity(0.15) : AppTheme.primaryColor.withOpacity(0.1),
                      width: 1.5,
                    ),
                  ),
                  child: Icon(
                    statusIcon,
                    size: 38,
                    color: isUploaded ? statusColor : AppTheme.primaryColor,
                  ),
                ),
                if (isUploaded)
                  Positioned(
                    right: -4,
                    top: -4,
                    child: Container(
                      padding: const EdgeInsets.all(5),
                      decoration: BoxDecoration(
                        color: statusColor,
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white, width: 2),
                      ),
                      child: Icon(
                        status == 'Verified' ? Icons.check : Icons.access_time_rounded,
                        color: Colors.white,
                        size: 12,
                      ),
                    ),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
