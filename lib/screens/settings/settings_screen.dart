import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../models/user_model.dart';
import '../../services/profile_service.dart';
import '../../routes/app_routes.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final ProfileService _profileService = ProfileService();
  late UserModel _user;

  @override
  void initState() {
    super.initState();
    _user = _profileService.getUser();
    _profileService.addListener(_onProfileChanged);
  }

  @override
  void dispose() {
    _profileService.removeListener(_onProfileChanged);
    super.dispose();
  }

  void _onProfileChanged() {
    if (mounted) {
      setState(() {
        _user = _profileService.getUser();
      });
    }
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

  void _showChangeLanguageDialog() {
    final languages = ["English", "Hindi", "Marathi", "Spanish", "French"];
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          backgroundColor: Colors.white,
          surfaceTintColor: Colors.transparent,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
          title: const Text("Select Language", style: TextStyle(fontWeight: FontWeight.bold, color: AppTheme.textColorPrimary)),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: languages.map((lang) {
              final isSelected = _user.language == lang;
              return RadioListTile<String>(
                value: lang,
                groupValue: _user.language,
                title: Text(lang, style: TextStyle(fontWeight: isSelected ? FontWeight.bold : FontWeight.normal, color: AppTheme.textColorPrimary)),
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
              onPressed: () {
                Navigator.pop(context);
                Navigator.pushNamedAndRemoveUntil(context, AppRoutes.login, (route) => false);
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      appBar: AppBar(
        title: const Text("Settings", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: AppTheme.textColorPrimary)),
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
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
          children: [
            // Section: Notifications
            _buildSectionHeader("NOTIFICATIONS"),
            Container(
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
                  _buildSwitchRow(
                    title: "Push Notifications",
                    subtitle: "Receive alerts for refills & status updates",
                    value: _user.pushNotifications,
                    onChanged: (val) => _updatePreference('push', val),
                  ),
                  const Divider(height: 1, thickness: 0.5, indent: 16, endIndent: 16),
                  _buildSwitchRow(
                    title: "Email Notifications",
                    subtitle: "Receive order receipts & weekly summaries",
                    value: _user.emailNotifications,
                    onChanged: (val) => _updatePreference('email', val),
                  ),
                  const Divider(height: 1, thickness: 0.5, indent: 16, endIndent: 16),
                  _buildSwitchRow(
                    title: "SMS Notifications",
                    subtitle: "Receive delivery tracking codes on SMS",
                    value: _user.smsNotifications,
                    onChanged: (val) => _updatePreference('sms', val),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Section: Preferences
            _buildSectionHeader("GENERAL PREFERENCES"),
            Container(
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
              child: _buildListTile(
                icon: Icons.language_rounded,
                title: "App Language",
                value: _user.language,
                onTap: _showChangeLanguageDialog,
              ),
            ),

            const SizedBox(height: 24),

            // Section: Legal & Information
            _buildSectionHeader("LEGAL & INFO"),
            Container(
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
                  _buildListTile(
                    icon: Icons.privacy_tip_outlined,
                    title: "Privacy Policy",
                    value: "",
                    onTap: () {
                      _showTextDialog("Privacy Policy", "At MediLoop, your medical privacy is highly protected. All uploaded prescriptions and details are encrypted and parsed locally via secure pharmacy agent protocols. We do not sell or distribute personal medical history.");
                    },
                  ),
                  const Divider(height: 1, thickness: 0.5, indent: 16, endIndent: 16),
                  _buildListTile(
                    icon: Icons.info_outline_rounded,
                    title: "About App",
                    value: "v1.0.0",
                    onTap: () {
                      Navigator.pushNamed(context, AppRoutes.aboutApp);
                    },
                  ),
                ],
              ),
            ),

            const SizedBox(height: 36),

            // Logout Action
            AnimatedButtonWrapper(
              onPressed: _showLogoutDialog,
              child: Container(
                height: 52,
                width: double.infinity,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.red.shade300, width: 1.5),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.red.shade100.withOpacity(0.2),
                      blurRadius: 8,
                      offset: const Offset(0, 3),
                    ),
                  ],
                ),
                alignment: Alignment.center,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.logout_rounded, color: Colors.red.shade700, size: 20),
                    const SizedBox(width: 10),
                    Text(
                      "Logout Account",
                      style: TextStyle(color: Colors.red.shade700, fontWeight: FontWeight.bold, fontSize: 15),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(left: 8.0, bottom: 8.0, top: 4.0),
      child: Text(
        title,
        style: const TextStyle(
          color: AppTheme.primaryColor,
          fontWeight: FontWeight.bold,
          fontSize: 12,
          letterSpacing: 0.8,
        ),
      ),
    );
  }

  Widget _buildSwitchRow({
    required String title,
    required String subtitle,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return SwitchListTile(
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14.5, color: AppTheme.textColorPrimary)),
      subtitle: Text(subtitle, style: const TextStyle(color: AppTheme.textColorSecondary, fontSize: 12)),
      value: value,
      activeColor: AppTheme.primaryColor,
      onChanged: onChanged,
    );
  }

  Widget _buildListTile({
    required IconData icon,
    required String title,
    required String value,
    required VoidCallback onTap,
  }) {
    return ListTile(
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: AppTheme.secondaryColor.withOpacity(0.4),
          shape: BoxShape.circle,
        ),
        child: Icon(icon, color: AppTheme.primaryColor, size: 20),
      ),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14.5, color: AppTheme.textColorPrimary)),
      trailing: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (value.isNotEmpty)
            Text(
              value,
              style: const TextStyle(color: AppTheme.textColorSecondary, fontSize: 13, fontWeight: FontWeight.bold),
            ),
          const SizedBox(width: 4),
          const Icon(Icons.chevron_right_rounded, color: AppTheme.textColorSecondary),
        ],
      ),
      onTap: onTap,
    );
  }

  void _showTextDialog(String title, String content) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          backgroundColor: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
          title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold, color: AppTheme.textColorPrimary)),
          content: SingleChildScrollView(child: Text(content, style: const TextStyle(fontSize: 13, height: 1.5, color: AppTheme.textColorSecondary))),
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

// Custom button scale wrapper
class AnimatedButtonWrapper extends StatefulWidget {
  final VoidCallback? onPressed;
  final Widget child;

  const AnimatedButtonWrapper({
    super.key,
    required this.onPressed,
    required this.child,
  });

  @override
  State<AnimatedButtonWrapper> createState() => _AnimatedButtonWrapperState();
}

class _AnimatedButtonWrapperState extends State<AnimatedButtonWrapper>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scale;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 80),
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
        child: widget.child,
      ),
    );
  }
}
