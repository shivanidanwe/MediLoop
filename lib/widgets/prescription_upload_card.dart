import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import '../services/cart_service.dart';
import '../routes/app_routes.dart';
import 'liquid_glass_card.dart';

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
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final status = _cartService.prescriptionStatus;
    final isUploaded = status != "None";

    Color statusColor = AppTheme.royalBlue;
    IconData statusIcon = Icons.document_scanner_rounded;
    String statusLabel = "No Prescription Uploaded";

    if (status == "Uploaded") {
      statusColor = AppTheme.electricCyan;
      statusIcon = Icons.cloud_done_rounded;
      statusLabel = "Prescription Uploaded";
    } else if (status == "Verification Pending") {
      statusColor = AppTheme.warmYellow;
      statusIcon = Icons.hourglass_top_rounded;
      statusLabel = "Verification Pending";
    } else if (status == "Verified") {
      statusColor = AppTheme.mint;
      statusIcon = Icons.verified_rounded;
      statusLabel = "Verified by Pharmacist";
    }

    return LiquidGlassCard(
      borderRadius: 24,
      padding: const EdgeInsets.all(22),
      hasGlow: true,
      glowColor: AppTheme.royalBlue,
      onTap: () => Navigator.pushNamed(context, AppRoutes.uploadPrescription),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [AppTheme.royalBlue, AppTheme.electricCyan],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(
                      color: AppTheme.royalBlue.withOpacity(0.3),
                      blurRadius: 12,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: const Center(
                  child: Icon(Icons.receipt_long_rounded, color: Colors.white, size: 24),
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      "Upload Prescription",
                      style: TextStyle(
                        fontSize: 17,
                        fontWeight: FontWeight.w800,
                        color: AppTheme.midnightNavy,
                        letterSpacing: -0.3,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      isUploaded ? statusLabel : "AI reads doctor's Rx & adds medicines instantly",
                      style: TextStyle(
                        fontSize: 12,
                        color: isUploaded ? statusColor : AppTheme.textColorSecondary,
                        fontWeight: isUploaded ? FontWeight.w700 : FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppTheme.royalBlue.withOpacity(0.08),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.arrow_forward_ios_rounded, size: 14, color: AppTheme.royalBlue),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            decoration: BoxDecoration(
              color: AppTheme.royalBlue.withOpacity(0.04),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: AppTheme.royalBlue.withOpacity(0.12)),
            ),
            child: Row(
              children: [
                Icon(statusIcon, size: 18, color: statusColor),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    isUploaded
                        ? "Rx Status: $statusLabel"
                        : "Camera & Gallery scans supported • Fast Pharmacist Verification",
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: isUploaded ? AppTheme.midnightNavy : AppTheme.textColorSecondary,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
