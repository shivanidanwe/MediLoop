import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../routes/app_routes.dart';
import '../../services/cart_service.dart';

class OrderTrackingScreen extends StatefulWidget {
  const OrderTrackingScreen({super.key});

  @override
  State<OrderTrackingScreen> createState() => _OrderTrackingScreenState();
}

class _OrderTrackingScreenState extends State<OrderTrackingScreen> with SingleTickerProviderStateMixin {
  late AnimationController _pulseController;
  String? _selectedOrderId;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);
    CartService().fetchOrdersFromBackend();
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final String initialOrderId = (ModalRoute.of(context)?.settings.arguments as String?) ?? (CartService().lastOrder?.orderId ?? "ML-1001");
    final String currentOrderId = _selectedOrderId ?? initialOrderId;
    final PlacedOrder? order = CartService().getOrderById(currentOrderId);
    final allOrders = CartService().orders;
    final displayStatus = order?.status ?? "Preparing Order";

    final steps = [
      _TrackingStep(
        title: "Order Received",
        description: "Your order has been registered and is being processed.",
        time: "10:30 AM",
        status: StepStatus.completed,
      ),
      _TrackingStep(
        title: "Prescription Verified",
        description: "All pharmacy items have been approved by the pharmacist agent.",
        time: "10:32 AM",
        status: StepStatus.completed,
      ),
      _TrackingStep(
        title: "Preparing Order",
        description: "Items are being safely packed and sealed at our smart warehouse.",
        time: "In Progress",
        status: StepStatus.active,
      ),
      _TrackingStep(
        title: "Out for Delivery",
        description: "Our delivery partner is on the way to your address.",
        time: "",
        status: StepStatus.pending,
      ),
      _TrackingStep(
        title: "Delivered",
        description: "Order completed. Please verify package seals upon receipt.",
        time: "",
        status: StepStatus.pending,
      ),
    ];

    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      appBar: AppBar(
        title: Column(
          children: [
            const Text(
              "Track Order",
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: AppTheme.textColorPrimary),
            ),
            const SizedBox(height: 2),
            Text(
              "Order ID: $currentOrderId",
              style: const TextStyle(fontSize: 12, color: AppTheme.textColorSecondary),
            ),
          ],
        ),
        backgroundColor: Colors.transparent,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        foregroundColor: AppTheme.textColorPrimary,
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 18, color: AppTheme.textColorPrimary),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          child: Column(
            children: [
              // Order Switcher if patient has multiple placed orders
              if (allOrders.length > 1)
                Container(
                  margin: const EdgeInsets.fromLTRB(20, 4, 20, 6),
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: Colors.grey.shade200),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.swap_horiz_rounded, size: 18, color: AppTheme.primaryColor),
                      const SizedBox(width: 8),
                      const Text(
                        "Order History: ",
                        style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.textColorPrimary),
                      ),
                      const SizedBox(width: 6),
                      Expanded(
                        child: DropdownButtonHideUnderline(
                          child: DropdownButton<String>(
                            value: currentOrderId,
                            isDense: true,
                            isExpanded: true,
                            items: allOrders.map((o) {
                              return DropdownMenuItem<String>(
                                value: o.orderId,
                                child: Text(
                                  "${o.orderId} (₹${o.grandTotal.toStringAsFixed(0)})",
                                  style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                                  overflow: TextOverflow.ellipsis,
                                ),
                              );
                            }).toList(),
                            onChanged: (val) {
                              if (val != null) {
                                setState(() => _selectedOrderId = val);
                              }
                            },
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

              // Current status hero summary card
              Container(
                margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: Colors.white,
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
                    Expanded(
                      child: Row(
                        children: [
                          const Icon(Icons.local_shipping_outlined, color: AppTheme.primaryColor, size: 22),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  "Current Status",
                                  style: TextStyle(color: AppTheme.textColorSecondary, fontSize: 11.5, fontWeight: FontWeight.bold),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  displayStatus,
                                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: AppTheme.textColorPrimary, letterSpacing: -0.3),
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: AppTheme.secondaryColor,
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: AppTheme.primaryColor.withOpacity(0.15), width: 0.5),
                      ),
                      child: Text(
                        displayStatus.toLowerCase().contains('delivered')
                            ? 'Delivered'
                            : displayStatus.toLowerCase().contains('approved')
                                ? 'Approved'
                                : 'In Progress',
                        style: const TextStyle(color: AppTheme.primaryColor, fontWeight: FontWeight.bold, fontSize: 11.5),
                      ),
                    ),
                  ],
                ),
              ),

              // Ordered Medicines & Prescription Extracted Text Card
              _buildOrderedItemsCard(order),

              // Timeline Area
              Container(
                margin: const EdgeInsets.fromLTRB(20, 6, 20, 16),
                padding: const EdgeInsets.fromLTRB(20, 24, 20, 4),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: const Color(0xFFE5E7EB).withOpacity(0.5), width: 1),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.01),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: ListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: steps.length,
                  itemBuilder: (context, index) {
                    final step = steps[index];
                    final isLast = index == steps.length - 1;

                    return _buildTimelineItem(step, isLast);
                  },
                ),
              ),

              // Back to Home Button
              Padding(
                padding: const EdgeInsets.fromLTRB(24, 8, 24, 28),
                child: AnimatedButtonWrapper(
                  onPressed: () {
                    Navigator.pushNamedAndRemoveUntil(context, AppRoutes.home, (route) => false);
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
                      "Back to Home",
                      style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white, fontSize: 15),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildOrderedItemsCard(PlacedOrder? order) {
    final items = order?.items ?? [];
    final prescriptionText = order?.prescriptionText ?? CartService().extractedPrescriptionText;

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 6),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFFE5E7EB).withOpacity(0.5), width: 1),
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
              Expanded(
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(6),
                      decoration: BoxDecoration(
                        color: AppTheme.secondaryColor.withOpacity(0.4),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.medication_rounded, color: AppTheme.primaryColor, size: 18),
                    ),
                    const SizedBox(width: 10),
                    Flexible(
                      child: Text(
                        "Ordered Medicines (${items.length})",
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: AppTheme.textColorPrimary),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
              ),
              if (order?.prescriptionId != null)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: const Color(0xFF2E7D32).withOpacity(0.12),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    "Rx #${order!.prescriptionId}",
                    style: const TextStyle(color: Color(0xFF2E7D32), fontWeight: FontWeight.bold, fontSize: 10.5),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 12),
          const Divider(height: 1),
          const SizedBox(height: 10),

          // Items list
          if (items.isNotEmpty)
            ...items.map((item) {
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            item.medicine.name,
                            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: AppTheme.textColorPrimary),
                          ),
                          Text(
                            "${item.medicine.dosageForm} • ${item.medicine.strength} (Qty: ${item.quantity})",
                            style: const TextStyle(fontSize: 11, color: AppTheme.textColorSecondary),
                          ),
                        ],
                      ),
                    ),
                    Text(
                      "₹${item.totalPrice.toStringAsFixed(0)}",
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: AppTheme.primaryColor),
                    ),
                  ],
                ),
              );
            })
          else
            const Text("No medicine items found in this order.", style: TextStyle(fontSize: 12, color: AppTheme.textColorSecondary)),

          // Extracted Prescription Text Box
          if (prescriptionText != null && prescriptionText.isNotEmpty) ...[
            const SizedBox(height: 14),
            _buildStructuredPrescriptionWidget(prescriptionText),
          ],
        ],
      ),
    );
  }

  Widget _buildStructuredPrescriptionWidget(String rawText) {
    // Check for stock notice in text or service
    final unavailList = <String>[];
    for (final u in CartService().unavailableMedicines) {
      if (!unavailList.contains(u)) unavailList.add(u);
    }
    if (rawText.contains("[Inventory Status Notice]") || rawText.contains("[Stock Notice]") || rawText.contains("not available")) {
      final match = RegExp(r'\[(?:Inventory Status Notice|Stock Notice)\]\s*([^\[\n\r]+)', caseSensitive: false).firstMatch(rawText);
      if (match != null) {
        final noticeText = match.group(1)?.trim() ?? "";
        if (noticeText.isNotEmpty && !unavailList.contains(noticeText)) {
          unavailList.add(noticeText);
        }
      } else if (rawText.toLowerCase().contains("formoterol") && !unavailList.any((m) => m.toLowerCase().contains("formoterol"))) {
        unavailList.add("Extracted medicine 'Formoterol' is not available in pharmacy inventory to add into cart.");
      }
    }

    // Clean text by removing stock notice brackets for display
    final displayText = rawText.replaceAll(RegExp(r'\[(?:Inventory Status Notice|Stock Notice)\][^\n]*', caseSensitive: false), '').trim();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 1. Notice Banner for Unavailable Medicines
        if (unavailList.isNotEmpty) ...[
          Container(
            width: double.infinity,
            margin: const EdgeInsets.only(bottom: 12),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            decoration: BoxDecoration(
              color: const Color(0xFFFFFBEB),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: const Color(0xFFFDE68A)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.warning_amber_rounded, size: 18, color: Color(0xFFD97706)),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        "Prescription Inventory Notice",
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 11.5, color: Color(0xFFB45309)),
                      ),
                      const SizedBox(height: 3),
                      ...unavailList.map((msg) => Padding(
                        padding: const EdgeInsets.only(bottom: 2),
                        child: Text(
                          "• $msg",
                          style: const TextStyle(fontSize: 11, color: Color(0xFF92400E), height: 1.3),
                        ),
                      )),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],

        // 2. Structured Prescription Details Card
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: const Color(0xFFF8FAFC),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: const Color(0xFFCBD5E1)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.assignment_outlined, size: 16, color: AppTheme.primaryColor),
                      SizedBox(width: 6),
                      Text(
                        "Structured Prescription Record",
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: AppTheme.textColorPrimary),
                      ),
                    ],
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: AppTheme.primaryColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: const Text(
                      "Verified AI Extraction",
                      style: TextStyle(fontSize: 9.5, fontWeight: FontWeight.bold, color: AppTheme.primaryColor),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 10),
              const Divider(height: 1, color: Color(0xFFE2E8F0)),
              const SizedBox(height: 10),
              _buildExactPrescriptionReportView(displayText),
            ],
          ),
        ),
      ],
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
        // Section Header
        spans.add(TextSpan(
          text: '$line\n',
          style: const TextStyle(
            fontWeight: FontWeight.w800,
            fontSize: 13,
            color: Color(0xFF0F172A),
            height: 1.8,
          ),
        ));
      } else if (trimmed.contains(':') && !RegExp(r'^\d+\.').hasMatch(trimmed)) {
        // Clinical Detail Field
        final colonIdx = line.indexOf(':');
        final label = line.substring(0, colonIdx + 1);
        final value = line.substring(colonIdx + 1);
        final isMissing = value.toLowerCase().contains('not mentioned in prescription') || value.toLowerCase().contains('unable to read clearly');

        spans.add(TextSpan(
          text: label,
          style: const TextStyle(
            fontWeight: FontWeight.w700,
            fontSize: 12,
            color: Color(0xFF334155),
            height: 1.5,
          ),
        ));
        spans.add(TextSpan(
          text: '$value\n',
          style: TextStyle(
            fontWeight: isMissing ? FontWeight.w400 : FontWeight.w500,
            fontSize: 12,
            color: isMissing ? const Color(0xFF64748B) : const Color(0xFF0F172A),
            fontStyle: isMissing ? FontStyle.italic : FontStyle.normal,
            height: 1.5,
          ),
        ));
      } else if (RegExp(r'^\d+\.').hasMatch(trimmed)) {
        // Numbered Medicine Item
        final isNeedsVerification = trimmed.toLowerCase().contains('(needs verification)');
        spans.add(TextSpan(
          text: '$line\n',
          style: TextStyle(
            fontWeight: FontWeight.w600,
            fontSize: 11.5,
            color: isNeedsVerification ? const Color(0xFFD97706) : const Color(0xFF1E293B),
            height: 1.6,
          ),
        ));
      } else {
        // Normal line or empty space
        spans.add(TextSpan(
          text: '$line\n',
          style: const TextStyle(
            fontWeight: FontWeight.normal,
            fontSize: 12,
            color: Color(0xFF334155),
            height: 1.5,
          ),
        ));
      }
    }

    return SelectableText.rich(
      TextSpan(children: spans),
    );
  }

  Widget _buildTimelineItem(_TrackingStep step, bool isLast) {
    Widget dotWidget;

    switch (step.status) {
      case StepStatus.completed:
        dotWidget = Container(
          width: 26,
          height: 26,
          decoration: const BoxDecoration(
            color: AppTheme.primaryColor,
            shape: BoxShape.circle,
          ),
          child: const Icon(Icons.check, color: Colors.white, size: 14),
        );
        break;
      case StepStatus.active:
        dotWidget = ScaleTransition(
          scale: Tween(begin: 0.92, end: 1.12).animate(
            CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
          ),
          child: Container(
            width: 26,
            height: 26,
            decoration: BoxDecoration(
              color: AppTheme.primaryColor.withOpacity(0.2),
              shape: BoxShape.circle,
            ),
            child: Center(
              child: Container(
                width: 12,
                height: 12,
                decoration: const BoxDecoration(
                  color: AppTheme.primaryColor,
                  shape: BoxShape.circle,
                ),
              ),
            ),
          ),
        );
        break;
      case StepStatus.pending:
        dotWidget = Container(
          width: 26,
          height: 26,
          decoration: BoxDecoration(
            color: Colors.white,
            border: Border.all(color: Colors.grey.shade300, width: 2),
            shape: BoxShape.circle,
          ),
        );
        break;
    }

    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Indicator column (dot + line)
          Column(
            children: [
              dotWidget,
              if (!isLast)
                Expanded(
                  child: Container(
                    width: 2,
                    margin: const EdgeInsets.symmetric(vertical: 4),
                    color: step.status == StepStatus.completed ? AppTheme.primaryColor : Colors.grey.shade200,
                  ),
                ),
            ],
          ),
          const SizedBox(width: 18),

          // Content Column
          Expanded(
            child: Padding(
              padding: const EdgeInsets.only(bottom: 24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        step.title,
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 14.5,
                          color: step.status == StepStatus.pending ? Colors.grey.shade500 : AppTheme.textColorPrimary,
                          letterSpacing: -0.2,
                        ),
                      ),
                      if (step.time.isNotEmpty)
                        Text(
                          step.time,
                          style: TextStyle(
                            color: step.status == StepStatus.active ? AppTheme.primaryColor : AppTheme.textColorSecondary,
                            fontSize: 11.5,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    step.description,
                    style: TextStyle(
                      color: step.status == StepStatus.pending ? Colors.grey.shade400 : Colors.grey.shade600,
                      fontSize: 12.5,
                      height: 1.4,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

enum StepStatus { completed, active, pending }

class _TrackingStep {
  final String title;
  final String description;
  final String time;
  final StepStatus status;

  _TrackingStep({
    required this.title,
    required this.description,
    required this.time,
    required this.status,
  });
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
