import 'dart:convert';
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../../core/constants/api_config.dart';
import '../../core/theme/app_theme.dart';
import '../../models/medicine_model.dart';
import '../../services/auth_service.dart';
import '../../services/cart_service.dart';

class AIChatScreen extends StatefulWidget {
  const AIChatScreen({super.key});

  @override
  State<AIChatScreen> createState() => _AIChatScreenState();
}

class _AIChatScreenState extends State<AIChatScreen> {
  final TextEditingController _inputController = TextEditingController();
  final List<_ChatMessage> _messages = [];
  bool _isTyping = false;
  final ScrollController _scrollController = ScrollController();
  final CartService _cartService = CartService();

  @override
  void initState() {
    super.initState();
  }

  @override
  void dispose() {
    _inputController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _sendMessage() {
    final text = _inputController.text.trim();
    if (text.isEmpty) return;

    _inputController.clear();
    _addUserMessage(text);
  }

  void _addUserMessage(String text) {
    setState(() {
      _messages.add(_ChatMessage(text: text, isUser: true));
      _isTyping = true;
    });
    _scrollToBottom();

    // Process AI response
    _processAIResponse(text);
  }

  void _processAIResponse(String userText) async {
    String replyText = "";
    Map<String, dynamic>? orderDraft;

    try {
      final token = await AuthService().getToken();
      final response = await http.post(
        Uri.parse('${ApiConfig.baseUrl}/ai/chat'),
        headers: ApiConfig.headers(token),
        body: jsonEncode({'message': userText}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        replyText = data['reply'] ?? "";
        if (data['order_draft'] != null) {
          orderDraft = Map<String, dynamic>.from(data['order_draft']);
        }
      } else {
        replyText = "I encountered an error connecting to MediLoop assistant. Please try again.";
      }
    } catch (_) {
      replyText = "Unable to reach MediLoop services. Please check your network connection.";
    }

    if (!mounted) return;

    setState(() {
      _isTyping = false;
      _messages.add(_ChatMessage(
        text: replyText,
        isUser: false,
        orderDraft: orderDraft,
      ));
    });
    _scrollToBottom();
  }

  Future<void> _confirmOrderDraft(String draftId) async {
    setState(() {
      _isTyping = true;
    });

    try {
      final token = await AuthService().getToken();
      final response = await http.post(
        Uri.parse('${ApiConfig.baseUrl}/ai/orders/confirm'),
        headers: ApiConfig.headers(token),
        body: jsonEncode({
          'draft_id': draftId,
          'idempotency_key': 'key_$draftId',
          'payment_method': 'COD'
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = jsonDecode(response.body);
        final orderNum = data['order_number'] ?? 'N/A';
        final total = (data['total_amount'] ?? 0.0).toStringAsFixed(2);
        setState(() {
          _isTyping = false;
          _messages.add(_ChatMessage(
            text: "✅ Order #$orderNum has been placed successfully for ₹$total! It is now pending pharmacist verification.",
            isUser: false,
          ));
        });
      } else {
        final err = jsonDecode(response.body);
        setState(() {
          _isTyping = false;
          _messages.add(_ChatMessage(
            text: "Failed to place order: ${err['detail'] ?? 'Verification failed'}",
            isUser: false,
          ));
        });
      }
    } catch (e) {
      setState(() {
        _isTyping = false;
        _messages.add(_ChatMessage(
          text: "Network error while placing order. Please try again.",
          isUser: false,
        ));
      });
    }
    _scrollToBottom();
  }

  void _simulateVoiceInput() {
    final voiceTextController = TextEditingController(text: "Order my diabetes medicine");

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
      ),
      builder: (modalContext) {
        return Padding(
          padding: EdgeInsets.only(
            bottom: MediaQuery.of(modalContext).viewInsets.bottom,
            top: 24,
            left: 20,
            right: 20,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 38,
                height: 4,
                margin: const EdgeInsets.only(bottom: 16),
                decoration: BoxDecoration(
                  color: Colors.grey.shade300,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              const Text(
                "Voice Speech Recognition",
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 17,
                  color: AppTheme.textColorPrimary,
                ),
              ),
              const SizedBox(height: 6),
              const Text(
                "Review or edit your spoken message before sending to the assistant.",
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 12.5, color: Colors.grey),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: voiceTextController,
                maxLines: 2,
                autofocus: true,
                decoration: InputDecoration(
                  labelText: "Recognized Voice Text (Editable)",
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(14)),
                  filled: true,
                  fillColor: Colors.grey.shade50,
                ),
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                children: [
                  ActionChip(
                    label: const Text("Order diabetes medicine"),
                    onPressed: () => voiceTextController.text = "Order my diabetes medicine",
                  ),
                  ActionChip(
                    label: const Text("Order BP medicine"),
                    onPressed: () => voiceTextController.text = "Order my BP medicine",
                  ),
                  ActionChip(
                    label: const Text("Check allergies"),
                    onPressed: () => voiceTextController.text = "What allergies are recorded in my profile?",
                  ),
                ],
              ),
              const SizedBox(height: 20),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => Navigator.pop(modalContext),
                      style: OutlinedButton.styleFrom(
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        padding: const EdgeInsets.symmetric(vertical: 12),
                      ),
                      child: const Text("Cancel"),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () {
                        final spokenText = voiceTextController.text.trim();
                        Navigator.pop(modalContext);
                        if (spokenText.isNotEmpty) {
                          _addUserMessage(spokenText);
                        }
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.primaryColor,
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        padding: const EdgeInsets.symmetric(vertical: 12),
                      ),
                      child: const Text("Send Query", style: TextStyle(fontWeight: FontWeight.bold)),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      extendBodyBehindAppBar: true,
      appBar: PreferredSize(
        preferredSize: const Size.fromHeight(66),
        child: ClipRect(
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 12, sigmaY: 12),
            child: AppBar(
              backgroundColor: Colors.white.withOpacity(0.75),
              elevation: 0,
              scrolledUnderElevation: 0,
              foregroundColor: AppTheme.textColorPrimary,
              centerTitle: false,
              title: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: AppTheme.secondaryColor.withOpacity(0.6),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      Icons.auto_awesome_rounded,
                      color: AppTheme.primaryColor,
                      size: 18,
                    ),
                  ),
                  const SizedBox(width: 12),
                  const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        "AI Health Companion",
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                          color: AppTheme.textColorPrimary,
                          letterSpacing: -0.3,
                        ),
                      ),
                      Text(
                        "Your Healthcare Companion",
                        style: TextStyle(
                          fontSize: 11,
                          color: AppTheme.textColorSecondary,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              bottom: PreferredSize(
                preferredSize: const Size.fromHeight(1),
                child: Container(
                  color: Colors.grey.shade200.withOpacity(0.5),
                  height: 1,
                ),
              ),
            ),
          ),
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: _messages.isEmpty ? _buildEmptyWelcomeState() : _buildChatList(),
            ),
            if (_isTyping) _buildTypingIndicator(),
            _buildInputArea(),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyWelcomeState() {
    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(),
      padding: const EdgeInsets.only(top: 100, left: 32, right: 32, bottom: 24),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Empty State Illustration
          TweenAnimationBuilder<double>(
            tween: Tween(begin: 0.0, end: 1.0),
            duration: const Duration(milliseconds: 700),
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
                painter: AIChatIllustrationPainter(
                  primaryColor: AppTheme.primaryColor,
                  secondaryColor: AppTheme.secondaryColor,
                  accentColor: AppTheme.accentColor,
                ),
              ),
            ),
          ),
          const SizedBox(height: 28),
          
          Text(
            "How can I help you today?",
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  fontSize: 20,
                  color: AppTheme.textColorPrimary,
                  letterSpacing: -0.5,
                ),
          ),
          const SizedBox(height: 10),
          const Text(
            "I can search medicines, translate prescriptions, set refill schedules or add items directly to your cart.",
            textAlign: TextAlign.center,
            style: TextStyle(
              color: AppTheme.textColorSecondary,
              fontSize: 13.5,
              height: 1.45,
            ),
          ),
          const SizedBox(height: 36),
          
          // Quick action prompt chips
          const Align(
            alignment: Alignment.centerLeft,
            child: Padding(
              padding: EdgeInsets.only(left: 8.0, bottom: 12),
              child: Text(
                "SUGGESTIONS",
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 11,
                  color: AppTheme.primaryColor,
                  letterSpacing: 0.6,
                ),
              ),
            ),
          ),
          
          Wrap(
            spacing: 12,
            runSpacing: 12,
            alignment: WrapAlignment.start,
            children: [
              _buildQuickPromptChip("Order Crocin 650", Icons.add_shopping_cart_rounded),
              _buildQuickPromptChip("Find an Antibiotic", Icons.science_outlined),
              _buildQuickPromptChip("Remind me of refills", Icons.alarm_rounded),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildQuickPromptChip(String label, IconData icon) {
    return ActionChip(
      avatar: Icon(icon, color: AppTheme.primaryColor, size: 14),
      label: Text(label),
      onPressed: () => _addUserMessage(label),
      backgroundColor: Colors.white,
      elevation: 0,
      side: BorderSide(color: AppTheme.primaryColor.withOpacity(0.12), width: 1),
      labelStyle: const TextStyle(
        color: AppTheme.textColorPrimary,
        fontWeight: FontWeight.w600,
        fontSize: 12.5,
      ),
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
    );
  }

  Widget _buildChatList() {
    return ListView.builder(
      controller: _scrollController,
      physics: const BouncingScrollPhysics(),
      padding: const EdgeInsets.only(top: 86, left: 16, right: 16, bottom: 16),
      itemCount: _messages.length,
      itemBuilder: (context, index) {
        final msg = _messages[index];
        return _buildMessageRow(msg);
      },
    );
  }

  Widget _buildMessageRow(_ChatMessage msg) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 18.0),
      child: Column(
        crossAxisAlignment: msg.isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: msg.isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (!msg.isUser) ...[
                Container(
                  margin: const EdgeInsets.only(top: 2),
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(
                    color: AppTheme.secondaryColor.withOpacity(0.6),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.auto_awesome_rounded,
                    color: AppTheme.primaryColor,
                    size: 14,
                  ),
                ),
                const SizedBox(width: 8),
              ],
              Flexible(
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.72),
                  decoration: BoxDecoration(
                    color: msg.isUser ? AppTheme.primaryColor : Colors.white,
                    borderRadius: BorderRadius.only(
                      topLeft: const Radius.circular(20),
                      topRight: const Radius.circular(20),
                      bottomLeft: msg.isUser ? const Radius.circular(20) : const Radius.circular(4),
                      bottomRight: msg.isUser ? const Radius.circular(4) : const Radius.circular(20),
                    ),
                    boxShadow: !msg.isUser
                        ? [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.03),
                              blurRadius: 10,
                              offset: const Offset(0, 4),
                            ),
                          ]
                        : [
                            BoxShadow(
                              color: AppTheme.primaryColor.withOpacity(0.18),
                              blurRadius: 8,
                              offset: const Offset(0, 3),
                            ),
                          ],
                    border: !msg.isUser
                        ? Border.all(color: Colors.grey.shade100, width: 1)
                        : null,
                  ),
                  child: Text(
                    msg.text,
                    style: TextStyle(
                      color: msg.isUser ? Colors.white : AppTheme.textColorPrimary,
                      fontSize: 14.5,
                      height: 1.45,
                    ),
                  ),
                ),
              ),
            ],
          ),
          if (!msg.isUser && msg.orderDraft != null) ...[
            Padding(
              padding: const EdgeInsets.only(left: 36.0, top: 10.0),
              child: _buildOrderDraftCard(msg.orderDraft!),
            ),
          ],
          if (!msg.isUser && msg.suggestedMedicine != null) ...[
            Padding(
              padding: const EdgeInsets.only(left: 36.0, top: 10.0),
              child: _buildInteractiveMedicineCard(msg.suggestedMedicine!),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildOrderDraftCard(Map<String, dynamic> draft) {
    final draftId = draft['draft_id']?.toString() ?? '';
    final medName = draft['medicine_name']?.toString() ?? 'Medicine';
    final strength = draft['strength']?.toString() ?? '';
    final form = draft['dosage_form']?.toString() ?? 'Tablet';
    final qty = draft['quantity'] ?? 1;
    final total = (draft['total_price'] ?? 0.0).toString();
    final pharmacy = draft['pharmacy_name']?.toString() ?? 'MediLoop Partner Pharmacy';
    final rxStatus = draft['prescription_status']?.toString() ?? 'Prescription Checked';
    bool isConfirmed = draft['is_confirmed'] == true;

    return StatefulBuilder(
      builder: (context, setCardState) {
        return Container(
          width: 290,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.06),
                blurRadius: 14,
                offset: const Offset(0, 4),
              ),
            ],
            border: Border.all(
              color: isConfirmed ? Colors.green : AppTheme.primaryColor.withOpacity(0.2),
              width: 1.5,
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: isConfirmed ? Colors.green.shade50 : AppTheme.primaryColor.withOpacity(0.08),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      isConfirmed ? "ORDER CONFIRMED" : "PROPOSED ORDER DRAFT",
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                        color: isConfirmed ? Colors.green.shade800 : AppTheme.primaryColor,
                        letterSpacing: 0.5,
                      ),
                    ),
                  ),
                  Text(
                    "₹$total",
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: AppTheme.primaryColor,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                medName,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: AppTheme.textColorPrimary,
                ),
              ),
              Text(
                "$strength • $form (Qty: $qty)",
                style: const TextStyle(
                  fontSize: 12.5,
                  color: AppTheme.textColorSecondary,
                ),
              ),
              const SizedBox(height: 10),
              Divider(color: Colors.grey.shade200, height: 1),
              const SizedBox(height: 10),
              Row(
                children: [
                  const Icon(Icons.storefront_outlined, size: 14, color: Colors.grey),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Text(
                      pharmacy,
                      style: const TextStyle(fontSize: 11.5, color: Colors.black87),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Row(
                children: [
                  Icon(
                    rxStatus.contains("Valid") || rxStatus.contains("Checked") ? Icons.verified_outlined : Icons.info_outline,
                    size: 14,
                    color: rxStatus.contains("Valid") || rxStatus.contains("Checked") ? Colors.green : Colors.blue,
                  ),
                  const SizedBox(width: 6),
                  Text(
                    rxStatus,
                    style: TextStyle(
                      fontSize: 11.5,
                      fontWeight: FontWeight.w600,
                      color: rxStatus.contains("Valid") || rxStatus.contains("Checked") ? Colors.green.shade700 : Colors.blue.shade700,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 14),
              if (!isConfirmed) ...[
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () async {
                      setCardState(() {
                        isConfirmed = true;
                        draft['is_confirmed'] = true;
                      });
                      await _confirmOrderDraft(draftId);
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.primaryColor,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      padding: const EdgeInsets.symmetric(vertical: 10),
                    ),
                    child: const Text("Confirm and Place Order", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                  ),
                ),
                const SizedBox(height: 6),
                SizedBox(
                  width: double.infinity,
                  child: TextButton(
                    onPressed: () {
                      _addUserMessage("Cancel draft");
                    },
                    style: TextButton.styleFrom(
                      foregroundColor: Colors.grey.shade700,
                      padding: const EdgeInsets.symmetric(vertical: 6),
                    ),
                    child: const Text("Cancel Draft", style: TextStyle(fontSize: 12)),
                  ),
                ),
              ] else ...[
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  decoration: BoxDecoration(
                    color: Colors.green.shade50,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  alignment: Alignment.center,
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.check_circle_rounded, color: Colors.green, size: 16),
                      const SizedBox(width: 6),
                      Text("Submitted to Pharmacy", style: TextStyle(color: Colors.green.shade800, fontWeight: FontWeight.bold, fontSize: 12)),
                    ],
                  ),
                ),
              ],
            ],
          ),
        );
      },
    );
  }

  Widget _buildInteractiveMedicineCard(Medicine med) {
    bool isAdded = false;

    return StatefulBuilder(
      builder: (context, setCardState) {
        return Container(
          width: 250,
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.04),
                blurRadius: 12,
                offset: const Offset(0, 4),
              ),
            ],
            border: Border.all(color: AppTheme.primaryColor.withOpacity(0.12), width: 1),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: 48,
                    height: 48,
                    decoration: BoxDecoration(
                      color: AppTheme.secondaryColor.withOpacity(0.4),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(
                      med.dosageForm.toLowerCase() == 'tablet'
                          ? Icons.tablet_rounded
                          : Icons.medication_liquid_rounded,
                      color: AppTheme.primaryColor,
                      size: 22,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          med.name,
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                            color: AppTheme.textColorPrimary,
                            letterSpacing: -0.2,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 2),
                        Text(
                          "${med.dosageForm} • ${med.strength}",
                          style: const TextStyle(
                            color: AppTheme.textColorSecondary,
                            fontSize: 11.5,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    "₹${med.price.toStringAsFixed(2)}",
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 15,
                      color: AppTheme.primaryColor,
                    ),
                  ),
                  if (med.prescriptionRequired)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                      decoration: BoxDecoration(
                        color: Colors.red.shade50,
                        borderRadius: BorderRadius.circular(6),
                        border: Border.all(color: Colors.red.shade100, width: 0.5),
                      ),
                      child: const Row(
                        children: [
                          Icon(Icons.assignment_late_rounded, color: Colors.red, size: 10),
                          SizedBox(width: 3),
                          Text(
                            "Rx Req",
                            style: TextStyle(
                              color: Colors.red,
                              fontSize: 9,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
              const Divider(height: 20, thickness: 0.5),
              
              // Custom scale feedback button
              AnimatedButtonWrapper(
                onPressed: isAdded
                    ? null
                    : () {
                        _cartService.addItem(med);
                        setCardState(() {
                          isAdded = true;
                        });
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text('Added ${med.name} to cart!'),
                            backgroundColor: AppTheme.primaryColor,
                            behavior: SnackBarBehavior.floating,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                          ),
                        );
                      },
                child: Container(
                  width: double.infinity,
                  height: 38,
                  decoration: BoxDecoration(
                    color: isAdded ? Colors.grey.shade100 : AppTheme.primaryColor,
                    borderRadius: BorderRadius.circular(10),
                    border: isAdded ? Border.all(color: Colors.grey.shade200) : null,
                  ),
                  alignment: Alignment.center,
                  child: Text(
                    isAdded ? "Added to Cart ✓" : "Add to Cart",
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.bold,
                      color: isAdded ? AppTheme.textColorSecondary : Colors.white,
                    ),
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildTypingIndicator() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(6),
            decoration: BoxDecoration(
              color: AppTheme.secondaryColor.withOpacity(0.6),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.auto_awesome_rounded,
              color: AppTheme.primaryColor,
              size: 14,
            ),
          ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(20),
                topRight: Radius.circular(20),
                bottomRight: Radius.circular(20),
                bottomLeft: Radius.circular(4),
              ),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.02),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
              border: Border.all(color: Colors.grey.shade100, width: 1),
            ),
            child: const Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                ThreeDotPulse(),
                SizedBox(width: 10),
                Text(
                  "Companion is processing...",
                  style: TextStyle(
                    color: AppTheme.textColorSecondary,
                    fontSize: 12.5,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 16,
            offset: const Offset(0, -4),
          ),
        ],
        border: Border(top: BorderSide(color: Colors.grey.shade100, width: 1)),
      ),
      child: Row(
        children: [
          Expanded(
            child: Container(
              height: 48,
              decoration: BoxDecoration(
                color: AppTheme.backgroundColor,
                borderRadius: BorderRadius.circular(24),
                border: Border.all(color: Colors.grey.shade200.withOpacity(0.8), width: 1),
              ),
              child: TextField(
                controller: _inputController,
                onSubmitted: (_) => _sendMessage(),
                style: const TextStyle(fontSize: 14, color: AppTheme.textColorPrimary),
                decoration: InputDecoration(
                  hintText: "Ask about medicines, dosage, refills...",
                  hintStyle: TextStyle(color: AppTheme.textColorSecondary.withOpacity(0.8), fontSize: 13.5),
                  border: InputBorder.none,
                  enabledBorder: InputBorder.none,
                  focusedBorder: InputBorder.none,
                  contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 10),
                ),
              ),
            ),
          ),
          const SizedBox(width: 10),
          
          // Voice Mic Button
          AnimatedButtonWrapper(
            onPressed: _simulateVoiceInput,
            child: Container(
              height: 44,
              width: 44,
              decoration: BoxDecoration(
                color: AppTheme.secondaryColor.withOpacity(0.5),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.mic_rounded,
                color: AppTheme.primaryColor,
                size: 20,
              ),
            ),
          ),
          const SizedBox(width: 8),
          
          // Send Button
          AnimatedButtonWrapper(
            onPressed: _sendMessage,
            child: Container(
              height: 44,
              width: 44,
              decoration: const BoxDecoration(
                color: AppTheme.primaryColor,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: AppTheme.primaryColor,
                    blurRadius: 8,
                    offset: Offset(0, 3),
                  ),
                ],
              ),
              child: const Icon(
                Icons.send_rounded,
                color: Colors.white,
                size: 18,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ChatMessage {
  final String text;
  final bool isUser;
  final Medicine? suggestedMedicine;
  final Map<String, dynamic>? orderDraft;

  _ChatMessage({
    required this.text,
    required this.isUser,
    this.suggestedMedicine,
    this.orderDraft,
  });
}

// Stateful voice listening pulse badge
class VoicePulse extends StatefulWidget {
  const VoicePulse({super.key});

  @override
  State<VoicePulse> createState() => _VoicePulseState();
}

class _VoicePulseState extends State<VoicePulse> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    )..repeat(reverse: true);
    _animation = Tween<double>(begin: 0.9, end: 1.15).animate(
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
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Transform.scale(
          scale: _animation.value,
          child: child,
        );
      },
      child: Container(
        padding: const EdgeInsets.all(22),
        decoration: BoxDecoration(
          color: AppTheme.primaryColor.withOpacity(0.08),
          shape: BoxShape.circle,
        ),
        child: const Icon(
          Icons.mic_rounded,
          color: AppTheme.primaryColor,
          size: 38,
        ),
      ),
    );
  }
}

// Bouncing three dots animation widget
class ThreeDotPulse extends StatefulWidget {
  const ThreeDotPulse({super.key});

  @override
  State<ThreeDotPulse> createState() => _ThreeDotPulseState();
}

class _ThreeDotPulseState extends State<ThreeDotPulse> with TickerProviderStateMixin {
  late List<AnimationController> _controllers;
  late List<Animation<double>> _animations;

  @override
  void initState() {
    super.initState();
    _controllers = List.generate(3, (index) {
      return AnimationController(
        vsync: this,
        duration: const Duration(milliseconds: 300),
      );
    });

    _animations = _controllers.map((controller) {
      return Tween<double>(begin: 0.0, end: -5.0).animate(
        CurvedAnimation(
          parent: controller,
          curve: Curves.easeInOut,
        ),
      );
    }).toList();

    _startAnimations();
  }

  void _startAnimations() async {
    if (!mounted) return;
    for (int i = 0; i < 3; i++) {
      if (!mounted) return;
      await Future.delayed(const Duration(milliseconds: 100));
      if (!mounted) return;
      _controllers[i].repeat(reverse: true);
    }
  }

  @override
  void dispose() {
    for (var controller in _controllers) {
      controller.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: List.generate(3, (index) {
        return AnimatedBuilder(
          animation: _animations[index],
          builder: (context, child) {
            return Transform.translate(
              offset: Offset(0, _animations[index].value),
              child: child,
            );
          },
          child: Container(
            margin: const EdgeInsets.symmetric(horizontal: 2.5),
            width: 6,
            height: 6,
            decoration: const BoxDecoration(
              color: AppTheme.primaryColor,
              shape: BoxShape.circle,
            ),
          ),
        );
      }),
    );
  }
}

// General button wrap that scales on press
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

// Custom Painter drawing the stethoscope heart empty state illustration
class AIChatIllustrationPainter extends CustomPainter {
  final Color primaryColor;
  final Color secondaryColor;
  final Color accentColor;

  AIChatIllustrationPainter({
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

    // 2. Outer decorative dashed circle
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

    // 3. Draw a heart at the center
    final heartPaint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.fill;
    
    // Heart shadow
    final shadowPaint = Paint()
      ..color = Colors.black.withOpacity(0.04)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 6);
    
    // Heart Path
    final heartPath = Path();
    final double hSize = width * 0.35;
    final double topY = center.dy - hSize * 0.4;
    heartPath.moveTo(center.dx, center.dy - hSize * 0.1);
    heartPath.cubicTo(
      center.dx - hSize * 0.55, topY - hSize * 0.35,
      center.dx - hSize * 0.9, topY + hSize * 0.3,
      center.dx, center.dy + hSize * 0.6,
    );
    heartPath.cubicTo(
      center.dx + hSize * 0.9, topY + hSize * 0.3,
      center.dx + hSize * 0.55, topY - hSize * 0.35,
      center.dx, center.dy - hSize * 0.1,
    );
    heartPath.close();

    canvas.drawPath(heartPath, shadowPaint);
    canvas.drawPath(heartPath, heartPaint);

    // 4. Draw a medical cross inside the heart
    final crossPaint = Paint()
      ..color = primaryColor
      ..style = PaintingStyle.fill;
    
    const double cSize = 10.0;
    final crossRectHorizontal = Rect.fromCenter(center: center.translate(0, hSize * 0.1), width: cSize * 2.8, height: cSize * 0.9);
    final crossRectVertical = Rect.fromCenter(center: center.translate(0, hSize * 0.1), width: cSize * 0.9, height: cSize * 2.8);
    
    canvas.drawRRect(RRect.fromRectAndRadius(crossRectHorizontal, const Radius.circular(2)), crossPaint);
    canvas.drawRRect(RRect.fromRectAndRadius(crossRectVertical, const Radius.circular(2)), crossPaint);

    // 5. Draw a stethoscope tube looping around the heart
    final stethPaint = Paint()
      ..color = primaryColor.withOpacity(0.7)
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    final stethPath = Path();
    stethPath.moveTo(center.dx + hSize * 0.2, center.dy + hSize * 0.55);
    stethPath.quadraticBezierTo(
      center.dx + hSize * 0.6, center.dy + hSize * 0.8,
      center.dx + hSize * 0.7, center.dy + hSize * 0.2,
    );
    stethPath.quadraticBezierTo(
      center.dx + hSize * 0.8, center.dy - hSize * 0.4,
      center.dx + hSize * 0.2, center.dy - hSize * 0.65,
    );
    stethPath.quadraticBezierTo(
      center.dx - hSize * 0.4, center.dy - hSize * 0.85,
      center.dx - hSize * 0.75, center.dy - hSize * 0.4,
    );
    stethPath.quadraticBezierTo(
      center.dx - hSize * 0.9, center.dy + hSize * 0.1,
      center.dx - hSize * 0.5, center.dy + hSize * 0.6,
    );
    
    canvas.drawPath(stethPath, stethPaint);

    // 6. Stethoscope bell end
    final bellCenter = Offset(center.dx + hSize * 0.7, center.dy + hSize * 0.2);
    canvas.drawCircle(bellCenter, 10, Paint()..color = Colors.white..style = PaintingStyle.fill);
    canvas.drawCircle(bellCenter, 10, Paint()..color = primaryColor..style = PaintingStyle.stroke..strokeWidth = 2.5);
    canvas.drawCircle(bellCenter, 5, Paint()..color = accentColor..style = PaintingStyle.fill);

    // 7. Sparkling stars/plus particles
    final sparkPaint = Paint()
      ..color = accentColor
      ..style = PaintingStyle.fill;
    
    _drawSparkle(canvas, center.translate(-width * 0.28, -height * 0.28), 6, sparkPaint);
    _drawSparkle(canvas, center.translate(width * 0.32, -height * 0.22), 8, sparkPaint);
    _drawSparkle(canvas, center.translate(-width * 0.35, height * 0.2), 5, sparkPaint);
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
  bool shouldRepaint(covariant AIChatIllustrationPainter oldDelegate) {
    return oldDelegate.primaryColor != primaryColor ||
        oldDelegate.secondaryColor != secondaryColor ||
        oldDelegate.accentColor != accentColor;
  }
}
