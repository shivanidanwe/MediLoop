import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

class AboutAppScreen extends StatelessWidget {
  const AboutAppScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      appBar: AppBar(
        title: const Text("About MediLoop", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: AppTheme.textColorPrimary)),
        backgroundColor: Colors.transparent,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 18, color: AppTheme.textColorPrimary),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SafeArea(
        child: ListView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
          children: [
            const SizedBox(height: 12),
            // App Logo/Icon branding Hero
            Center(
              child: Column(
                children: [
                  Container(
                    padding: const EdgeInsets.all(22),
                    decoration: BoxDecoration(
                      color: AppTheme.secondaryColor.withOpacity(0.4),
                      shape: BoxShape.circle,
                      border: Border.all(color: AppTheme.primaryColor.withOpacity(0.2), width: 2),
                      boxShadow: [
                        BoxShadow(
                          color: AppTheme.primaryColor.withOpacity(0.08),
                          blurRadius: 16,
                          offset: const Offset(0, 6),
                        ),
                      ],
                    ),
                    child: const Icon(
                      Icons.medical_services_rounded,
                      size: 58,
                      color: AppTheme.primaryColor,
                    ),
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    "MediLoop App",
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 22,
                      color: AppTheme.textColorPrimary,
                      letterSpacing: -0.3,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                    decoration: BoxDecoration(
                      color: AppTheme.primaryColor.withOpacity(0.08),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Text(
                      "Version 1.0.0 (HackFusion MVP)",
                      style: TextStyle(color: AppTheme.primaryColor, fontSize: 12, fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),

            // Developers Panel
            _buildInfoSection(
              context,
              title: "DEVELOPERS",
              child: Container(
                padding: const EdgeInsets.all(18),
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
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: AppTheme.secondaryColor.withOpacity(0.4),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.code_rounded, color: AppTheme.primaryColor, size: 22),
                    ),
                    const SizedBox(width: 14),
                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            "Google DeepMind & AI Pharmacy Teams",
                            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14.5, color: AppTheme.textColorPrimary),
                          ),
                          SizedBox(height: 2),
                          Text(
                            "Built for HackFusion Hackathon 2026",
                            style: TextStyle(color: AppTheme.textColorSecondary, fontSize: 12),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Contact Support Details
            _buildInfoSection(
              context,
              title: "CONTACT & SUPPORT",
              child: Container(
                padding: const EdgeInsets.all(18),
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
                  children: [
                    _buildContactRow(Icons.email_outlined, "support@mediloop.ai"),
                    const Divider(height: 24, thickness: 0.5),
                    _buildContactRow(Icons.phone_outlined, "+1 (800) 555-LOOP"),
                    const Divider(height: 24, thickness: 0.5),
                    _buildContactRow(Icons.language_outlined, "www.mediloop.ai"),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Legal terms links
            _buildInfoSection(
              context,
              title: "LEGAL TERMS & CONDITIONS",
              child: Container(
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
                  children: [
                    _buildActionTile(context, "Privacy Policy", () {
                      _showTextDialog(
                        context,
                        "Privacy Policy",
                        "MediLoop encrypts all user profiles and medicine purchases. Uploaded scans of Doctor's prescriptions are processed by HIPAA-compliant secure autonomous AI services. No data is shared with unverified external suppliers.",
                      );
                    }),
                    const Divider(height: 1, thickness: 0.5, indent: 16, endIndent: 16),
                    _buildActionTile(context, "Terms & Conditions", () {
                      _showTextDialog(
                        context,
                        "Terms & Conditions",
                        "By purchasing from MediLoop Smart Pharmacy, you confirm you are uploading genuine prescriptions issued by registered medical professionals. Simulated actions in this MVP are for demonstration purposes only.",
                      );
                    }),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 40),

            const Center(
              child: Text(
                "© 2026 MediLoop. All rights reserved.",
                style: TextStyle(color: AppTheme.textColorSecondary, fontSize: 12, fontWeight: FontWeight.w600),
              ),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoSection(BuildContext context, {required String title, required Widget child}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(left: 8.0, bottom: 8.0),
          child: Text(
            title,
            style: const TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 12,
              color: AppTheme.primaryColor,
              letterSpacing: 0.8,
            ),
          ),
        ),
        child,
      ],
    );
  }

  Widget _buildContactRow(IconData icon, String detail) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: AppTheme.secondaryColor.withOpacity(0.4),
            shape: BoxShape.circle,
          ),
          child: Icon(icon, color: AppTheme.primaryColor, size: 18),
        ),
        const SizedBox(width: 14),
        Text(
          detail,
          style: const TextStyle(
            fontWeight: FontWeight.w600,
            fontSize: 14,
            color: AppTheme.textColorPrimary,
          ),
        ),
      ],
    );
  }

  Widget _buildActionTile(BuildContext context, String title, VoidCallback onTap) {
    return ListTile(
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      title: Text(
        title,
        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14.5, color: AppTheme.textColorPrimary),
      ),
      trailing: const Icon(Icons.chevron_right_rounded, color: AppTheme.textColorSecondary),
      onTap: onTap,
    );
  }

  void _showTextDialog(BuildContext context, String title, String content) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          backgroundColor: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
          title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold, color: AppTheme.textColorPrimary)),
          content: SingleChildScrollView(
            child: Text(
              content,
              style: const TextStyle(fontSize: 13, height: 1.5, color: AppTheme.textColorSecondary),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text("Close", style: TextStyle(color: AppTheme.primaryColor, fontWeight: FontWeight.bold)),
            )
          ],
        );
      },
    );
  }
}
