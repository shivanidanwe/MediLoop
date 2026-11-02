import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../routes/app_routes.dart';

class OrderSuccessScreen extends StatefulWidget {
  const OrderSuccessScreen({super.key});

  @override
  State<OrderSuccessScreen> createState() => _OrderSuccessScreenState();
}

class _OrderSuccessScreenState extends State<OrderSuccessScreen> with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    );
    _scaleAnimation = CurvedAnimation(
      parent: _animationController,
      curve: Curves.elasticOut,
    );
    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final String orderId = (ModalRoute.of(context)?.settings.arguments as String?) ?? "ML-8291";

    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, constraints) {
            return SingleChildScrollView(
              physics: const BouncingScrollPhysics(),
              child: ConstrainedBox(
                constraints: BoxConstraints(minHeight: constraints.maxHeight),
                child: IntrinsicHeight(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 24.0),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        const Spacer(),

                        // Premium Success Illustration
                        ScaleTransition(
                          scale: _scaleAnimation,
                          child: Center(
                            child: SizedBox(
                              width: 170,
                              height: 170,
                              child: CustomPaint(
                                painter: OrderSuccessIllustrationPainter(
                                  primaryColor: AppTheme.primaryColor,
                                  secondaryColor: AppTheme.secondaryColor,
                                  accentColor: AppTheme.accentColor,
                                ),
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(height: 36),

                        // Title
                        const Text(
                          "Order Confirmed",
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 24,
                            color: AppTheme.textColorPrimary,
                            letterSpacing: -0.5,
                          ),
                        ),
                        const SizedBox(height: 12),

                        // Description
                        Text(
                          "Your order has been received and registered with our pharmacy systems. The pharmacist is preparing your medicines.",
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: AppTheme.textColorSecondary.withOpacity(0.9),
                            fontSize: 14,
                            height: 1.45,
                          ),
                        ),
                        const SizedBox(height: 32),

                        // Order ID Card
                        Container(
                          padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
                          decoration: BoxDecoration(
                            color: AppTheme.cardColor,
                            borderRadius: BorderRadius.circular(24),
                            border: Border.all(color: const Color(0xFFE5E7EB).withOpacity(0.5), width: 1),
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withOpacity(0.015),
                                blurRadius: 12,
                                offset: const Offset(0, 6),
                              ),
                            ],
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              const Text(
                                "Order ID",
                                style: TextStyle(color: AppTheme.textColorSecondary, fontWeight: FontWeight.bold, fontSize: 13.5),
                              ),
                              Text(
                                orderId,
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 15.5,
                                  color: AppTheme.primaryColor,
                                  letterSpacing: 0.5,
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 16),
                        
                        Text(
                          "You will receive a confirmation notification shortly.",
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: AppTheme.textColorSecondary.withOpacity(0.8),
                            fontSize: 12.5,
                            fontWeight: FontWeight.w500,
                          ),
                        ),

                        const Spacer(),

                        // Primary Action
                        AnimatedButtonWrapper(
                          onPressed: () {
                            Navigator.pushReplacementNamed(
                              context,
                              AppRoutes.orderTracking,
                              arguments: orderId,
                            );
                          },
                          child: Container(
                            height: 52,
                            decoration: BoxDecoration(
                              color: AppTheme.primaryColor,
                              borderRadius: BorderRadius.circular(16),
                              boxShadow: [
                                BoxShadow(
                                  color: AppTheme.primaryColor.withOpacity(0.22),
                                  blurRadius: 10,
                                  offset: const Offset(0, 4),
                                ),
                              ],
                            ),
                            alignment: Alignment.center,
                            child: const Text(
                              "Track Order",
                              style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white, fontSize: 15),
                            ),
                          ),
                        ),
                        const SizedBox(height: 12),

                        // Secondary Action
                        AnimatedButtonWrapper(
                          onPressed: () {
                            Navigator.pushNamedAndRemoveUntil(
                              context,
                              AppRoutes.home,
                              (route) => false,
                            );
                          },
                          child: Container(
                            height: 52,
                            decoration: BoxDecoration(
                              color: Colors.transparent,
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(color: AppTheme.primaryColor, width: 2),
                            ),
                            alignment: Alignment.center,
                            child: const Text(
                              "Back to Home",
                              style: TextStyle(
                                color: AppTheme.primaryColor,
                                fontWeight: FontWeight.bold,
                                fontSize: 15,
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            );
          },
        ),
      ),
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

// Custom Painter drawing the Order Success illustration
class OrderSuccessIllustrationPainter extends CustomPainter {
  final Color primaryColor;
  final Color secondaryColor;
  final Color accentColor;

  OrderSuccessIllustrationPainter({
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

    // 3. Draw Medicine Package Box/Bag
    final bagPaint = Paint()
      ..color = primaryColor
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    final bagFill = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.fill;

    final bagPath = Path();
    final double bWidth = width * 0.40;
    final double bHeight = height * 0.38;
    final double topY = center.dy - bHeight * 0.4;
    final double bottomY = center.dy + bHeight * 0.5;

    bagPath.moveTo(center.dx - bWidth * 0.5, topY + 12);
    bagPath.quadraticBezierTo(center.dx - bWidth * 0.5, topY, center.dx - bWidth * 0.5 + 12, topY);
    bagPath.lineTo(center.dx + bWidth * 0.5 - 12, topY);
    bagPath.quadraticBezierTo(center.dx + bWidth * 0.5, topY, center.dx + bWidth * 0.5, topY + 12);
    bagPath.lineTo(center.dx + bWidth * 0.5, bottomY - 12);
    bagPath.quadraticBezierTo(center.dx + bWidth * 0.5, bottomY, center.dx + bWidth * 0.5 - 12, bottomY);
    bagPath.lineTo(center.dx - bWidth * 0.5 + 12, bottomY);
    bagPath.quadraticBezierTo(center.dx - bWidth * 0.5, bottomY, center.dx - bWidth * 0.5, bottomY - 12);
    bagPath.close();

    final shadowPaint = Paint()
      ..color = Colors.black.withOpacity(0.04)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 6);
    canvas.drawPath(bagPath.shift(const Offset(0, 4)), shadowPaint);
    canvas.drawPath(bagPath, bagFill);
    canvas.drawPath(bagPath, bagPaint);

    final crossPaint = Paint()
      ..color = primaryColor.withOpacity(0.12)
      ..style = PaintingStyle.fill;
    final double crossSize = bWidth * 0.35;
    
    canvas.drawRect(
      Rect.fromCenter(center: center.translate(0, 4), width: crossSize, height: crossSize * 0.35),
      crossPaint,
    );
    canvas.drawRect(
      Rect.fromCenter(center: center.translate(0, 4), width: crossSize * 0.35, height: crossSize),
      crossPaint,
    );

    final linePaint = Paint()
      ..color = primaryColor.withOpacity(0.2)
      ..strokeWidth = 2
      ..strokeCap = StrokeCap.round;
    canvas.drawLine(Offset(center.dx - bWidth * 0.5 + 10, topY + 20), Offset(center.dx + bWidth * 0.5 - 10, topY + 20), linePaint);

    // 4. Large Success Shield/Badge on bottom-right of package
    final double badgeRadius = width * 0.16;
    final badgeCenter = center.translate(bWidth * 0.45, bHeight * 0.4);
    
    final badgeShadow = Paint()
      ..color = Colors.black.withOpacity(0.08)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 4);
    canvas.drawCircle(badgeCenter.translate(0, 2), badgeRadius, badgeShadow);
    canvas.drawCircle(badgeCenter, badgeRadius, Paint()..color = Colors.white);
    canvas.drawCircle(badgeCenter, badgeRadius, Paint()..color = primaryColor..style = PaintingStyle.stroke..strokeWidth = 2.5);
    canvas.drawCircle(badgeCenter, badgeRadius - 4, Paint()..color = secondaryColor);

    final checkPaint = Paint()
      ..color = primaryColor
      ..strokeWidth = 3
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round
      ..style = PaintingStyle.stroke;
    
    final checkPath = Path();
    checkPath.moveTo(badgeCenter.dx - badgeRadius * 0.4, badgeCenter.dy);
    checkPath.lineTo(badgeCenter.dx - badgeRadius * 0.1, badgeCenter.dy + badgeRadius * 0.3);
    checkPath.lineTo(badgeCenter.dx + badgeRadius * 0.4, badgeCenter.dy - badgeRadius * 0.3);
    canvas.drawPath(checkPath, checkPaint);

    // 5. Floating Capsule (top left)
    canvas.save();
    canvas.translate(center.dx - bWidth * 0.65, center.dy - bHeight * 0.5);
    canvas.rotate(-0.4);
    
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

    final sparkPaint = Paint()
      ..color = accentColor
      ..style = PaintingStyle.fill;
    _drawSparkle(canvas, center.translate(width * 0.3, -height * 0.22), 5, sparkPaint);
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
  bool shouldRepaint(covariant OrderSuccessIllustrationPainter oldDelegate) {
    return oldDelegate.primaryColor != primaryColor ||
        oldDelegate.secondaryColor != secondaryColor ||
        oldDelegate.accentColor != accentColor;
  }
}
