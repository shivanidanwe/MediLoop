import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  List<Map<String, String>> _notifications = [];
  bool _isLoading = false;
  bool _hasFetched = false;

  @override
  void initState() {
    super.initState();
    _fetchNotifications();
  }

  Future<void> _fetchNotifications() async {
    setState(() {
      _isLoading = true;
    });

    await Future.delayed(const Duration(milliseconds: 1200));

    if (mounted) {
      setState(() {
        _notifications = [
          {
            "id": "1",
            "title": "Refill Alert: Crocin 650",
            "body": "Your Crocin 650 stock is low (estimated 3 days remaining). Reorder now with one tap.",
            "time": "Just Now",
            "type": "refill",
            "read": "false"
          },
          {
            "id": "2",
            "title": "Prescription Approved 📄",
            "body": "Your uploaded prescription has been verified by the autonomous pharmacy agent.",
            "time": "2 hours ago",
            "type": "prescription",
            "read": "false"
          },
          {
            "id": "3",
            "title": "Order Out for Delivery 📦",
            "body": "Order #ML-9281 containing Vitamins B12 has been prepared and is out for delivery.",
            "time": "Yesterday",
            "type": "delivery",
            "read": "true"
          }
        ];
        _isLoading = false;
        _hasFetched = true;
      });
    }
  }

  void _clearNotifications() {
    setState(() {
      _notifications.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      appBar: AppBar(
        title: const Text(
          "Notifications",
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: AppTheme.textColorPrimary),
        ),
        backgroundColor: Colors.transparent,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 18, color: AppTheme.textColorPrimary),
          onPressed: () => Navigator.pop(context),
        ),
        actions: _notifications.isNotEmpty
            ? [
                Padding(
                  padding: const EdgeInsets.only(right: 12.0),
                  child: Container(
                    decoration: BoxDecoration(
                      color: Colors.white,
                      shape: BoxShape.circle,
                      border: Border.all(color: Colors.grey.shade200),
                    ),
                    child: IconButton(
                      icon: const Icon(Icons.delete_sweep_outlined, color: Colors.grey, size: 20),
                      onPressed: _clearNotifications,
                    ),
                  ),
                )
              ]
            : null,
      ),
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _fetchNotifications,
          color: AppTheme.primaryColor,
          child: _isLoading
              ? _buildShimmerLoading()
              : _notifications.isEmpty
                  ? _buildEmptyState()
                  : _buildNotificationsList(),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return ListView(
      physics: const AlwaysScrollableScrollPhysics(),
      children: [
        SizedBox(height: MediaQuery.of(context).size.height * 0.16),
        Center(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 40.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Empty state illustration
                TweenAnimationBuilder<double>(
                  tween: Tween(begin: 0.0, end: 1.0),
                  duration: const Duration(milliseconds: 750),
                  curve: Curves.easeOutCubic,
                  builder: (context, value, child) {
                    return Opacity(
                      opacity: value,
                      child: Transform.scale(
                        scale: 0.88 + (value * 0.12),
                        child: child,
                      ),
                    );
                  },
                  child: SizedBox(
                    width: 170,
                    height: 170,
                    child: CustomPaint(
                      painter: NotificationsEmptyIllustrationPainter(
                        primaryColor: AppTheme.primaryColor,
                        secondaryColor: AppTheme.secondaryColor,
                        accentColor: AppTheme.accentColor,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 32),
                const Text(
                  "All Caught Up!",
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 20,
                    color: AppTheme.textColorPrimary,
                    letterSpacing: -0.5,
                  ),
                ),
                const SizedBox(height: 10),
                Text(
                  "You have read all notifications. Pull down to refresh and check for updates.",
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: AppTheme.textColorSecondary.withOpacity(0.9),
                    fontSize: 13.5,
                    height: 1.45,
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildShimmerLoading() {
    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      itemCount: 3,
      itemBuilder: (context, index) {
        return Container(
          margin: const EdgeInsets.only(bottom: 16),
          padding: const EdgeInsets.all(16),
          height: 106,
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: const Color(0xFFE5E7EB).withOpacity(0.4)),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Container(height: 14, width: 140, color: Colors.grey.shade100),
                    Container(height: 10, width: double.infinity, color: Colors.grey.shade100),
                    Container(height: 10, width: 70, color: Colors.grey.shade100),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildNotificationsList() {
    return ListView.builder(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      itemCount: _notifications.length,
      itemBuilder: (context, index) {
        final item = _notifications[index];
        final isUnread = item["read"] == "false";

        IconData icon;
        Color iconColor;

        switch (item["type"]) {
          case 'refill':
            icon = Icons.alarm_rounded;
            iconColor = Colors.orange.shade800;
            break;
          case 'prescription':
            icon = Icons.assignment_turned_in_rounded;
            iconColor = AppTheme.primaryColor;
            break;
          default:
            icon = Icons.local_shipping_rounded;
            iconColor = Colors.blue.shade800;
        }

        return Container(
          margin: const EdgeInsets.only(bottom: 16),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: isUnread ? AppTheme.secondaryColor.withOpacity(0.2) : Colors.white,
            borderRadius: BorderRadius.circular(24),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.015),
                blurRadius: 12,
                offset: const Offset(0, 6),
              ),
            ],
            border: Border.all(
              color: isUnread ? AppTheme.primaryColor.withOpacity(0.3) : const Color(0xFFE5E7EB).withOpacity(0.5),
              width: isUnread ? 1.5 : 1,
            ),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Icon Badge container
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: iconColor.withOpacity(0.12),
                  shape: BoxShape.circle,
                ),
                child: Icon(icon, color: iconColor, size: 20),
              ),
              const SizedBox(width: 14),

              // Detail text column
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Text(
                            item["title"]!,
                            style: TextStyle(
                              fontWeight: isUnread ? FontWeight.bold : FontWeight.w600,
                              fontSize: 14.5,
                              color: AppTheme.textColorPrimary,
                              letterSpacing: -0.2,
                            ),
                          ),
                        ),
                        if (isUnread)
                          Container(
                            width: 8,
                            height: 8,
                            decoration: const BoxDecoration(
                              color: AppTheme.primaryColor,
                              shape: BoxShape.circle,
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      item["body"]!,
                      style: const TextStyle(
                        color: AppTheme.textColorSecondary,
                        fontSize: 12.5,
                        height: 1.4,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          item["time"]!,
                          style: TextStyle(
                            color: AppTheme.textColorSecondary.withOpacity(0.7),
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        if (item["type"] == "refill")
                          InkWell(
                            onTap: () {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text("Initiating fast reorder...")),
                              );
                            },
                            child: const Text(
                              "Reorder Now",
                              style: TextStyle(
                                color: AppTheme.primaryColor,
                                fontWeight: FontWeight.bold,
                                fontSize: 11.5,
                              ),
                            ),
                          ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
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

// Custom Painter drawing the empty notifications illustration
class NotificationsEmptyIllustrationPainter extends CustomPainter {
  final Color primaryColor;
  final Color secondaryColor;
  final Color accentColor;

  NotificationsEmptyIllustrationPainter({
    required this.primaryColor,
    required this.secondaryColor,
    required this.accentColor,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final width = size.width;
    final height = size.height;
    final center = Offset(width / 2, height / 2);

    // 1. Soft background circle
    final bgPaint = Paint()
      ..color = secondaryColor.withOpacity(0.35)
      ..style = PaintingStyle.fill;
    canvas.drawCircle(center, width * 0.42, bgPaint);

    // 2. Dashed boundary ring
    final dotPaint = Paint()
      ..color = primaryColor.withOpacity(0.18)
      ..strokeWidth = 1.5
      ..style = PaintingStyle.stroke;

    final double radius = width * 0.46;
    const int dashCount = 32;
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

    // 3. Draw Alarm Bell Outline
    final bellPaint = Paint()
      ..color = primaryColor
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    final bellFill = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.fill;

    final bellPath = Path();
    final double bWidth = width * 0.38;
    final double bHeight = height * 0.35;
    final double topY = center.dy - bHeight * 0.45;
    final double bottomY = center.dy + bHeight * 0.35;

    // Draw modern bell bell-shape
    bellPath.moveTo(center.dx, topY);
    // Left curve down
    bellPath.quadraticBezierTo(center.dx - bWidth * 0.4, topY + bHeight * 0.15, center.dx - bWidth * 0.42, bottomY - 8);
    // Left flare corner
    bellPath.lineTo(center.dx - bWidth * 0.54, bottomY);
    bellPath.lineTo(center.dx + bWidth * 0.54, bottomY);
    // Right flare corner
    bellPath.lineTo(center.dx + bWidth * 0.42, bottomY - 8);
    // Right curve up
    bellPath.quadraticBezierTo(center.dx + bWidth * 0.4, topY + bHeight * 0.15, center.dx, topY);
    bellPath.close();

    // Box shadow under bell
    final shadowPaint = Paint()
      ..color = Colors.black.withOpacity(0.04)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 6);
    canvas.drawPath(bellPath.shift(const Offset(0, 4)), shadowPaint);
    canvas.drawPath(bellPath, bellFill);
    canvas.drawPath(bellPath, bellPaint);

    // Bell clapper clapper ball
    final clapperPaint = Paint()
      ..color = accentColor
      ..style = PaintingStyle.fill;
    canvas.drawArc(
      Rect.fromCenter(center: Offset(center.dx, bottomY), width: bWidth * 0.32, height: bWidth * 0.32),
      0,
      3.141592653589793, // bottom semi-circle
      true,
      clapperPaint,
    );

    // Bell top ring handle
    canvas.drawCircle(
      Offset(center.dx, topY - 4),
      6,
      Paint()..color = primaryColor..style = PaintingStyle.stroke..strokeWidth = 3,
    );

    // 4. Floating Check mark inside bell (clean insignia)
    final checkPaint = Paint()
      ..color = primaryColor.withOpacity(0.15)
      ..strokeWidth = 4
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round
      ..style = PaintingStyle.stroke;
    final checkPath = Path();
    checkPath.moveTo(center.dx - 12, center.dy - 2);
    checkPath.lineTo(center.dx - 3, center.dy + 7);
    checkPath.lineTo(center.dx + 12, center.dy - 7);
    canvas.drawPath(checkPath, checkPaint);

    // 5. Floating Capsule (top right)
    canvas.save();
    canvas.translate(center.dx + bWidth * 0.55, center.dy - bHeight * 0.4);
    canvas.rotate(0.4);
    
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromCenter(center: const Offset(0, 1), width: 8, height: 18),
        const Radius.circular(4),
      ),
      Paint()..color = Colors.black.withOpacity(0.04)..maskFilter = const MaskFilter.blur(BlurStyle.normal, 2),
    );

    final pillRectBottom = RRect.fromRectAndCorners(
      const Rect.fromLTWH(-4, 0, 8, 8),
      bottomLeft: const Radius.circular(4),
      bottomRight: const Radius.circular(4),
    );
    final pillRectTop = RRect.fromRectAndCorners(
      const Rect.fromLTWH(-4, -8, 8, 8),
      topLeft: const Radius.circular(4),
      topRight: const Radius.circular(4),
    );

    canvas.drawRRect(pillRectTop, Paint()..color = accentColor);
    canvas.drawRRect(pillRectBottom, Paint()..color = secondaryColor);

    canvas.drawLine(
      const Offset(-4, 0),
      const Offset(4, 0),
      Paint()..color = Colors.white..strokeWidth = 1,
    );
    canvas.restore();

    // Sparkles
    final sparkPaint = Paint()
      ..color = accentColor
      ..style = PaintingStyle.fill;
    _drawSparkle(canvas, center.translate(-width * 0.3, -height * 0.22), 5, sparkPaint);
  }

  void _drawSparkle(Canvas canvas, Offset offset, double size, Paint paint) {
    final path = Path();
    path.moveTo(offset.dx, offset.dy - size);
    path.quadraticBezierTo(offset.dx, offset.dy, offset.dx + size, offset.dy);
    path.quadraticBezierTo(offset.dx, offset.dy, offset.dx, offset.dy + size);
    path.quadraticBezierTo(offset.dx, offset.dy, offset.dx - size, offset.dy);
    path.quadraticBezierTo(offset.dx, offset.dy, offset.dx, offset.dy - size);
    path.close();
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant NotificationsEmptyIllustrationPainter oldDelegate) {
    return oldDelegate.primaryColor != primaryColor ||
        oldDelegate.secondaryColor != secondaryColor ||
        oldDelegate.accentColor != accentColor;
  }
}
