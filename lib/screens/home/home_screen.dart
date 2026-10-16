import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../models/user_model.dart';
import '../../models/refill_model.dart';
import '../../models/medicine_model.dart';
import '../../services/medicine_service.dart';
import '../../routes/app_routes.dart';
import '../../widgets/custom_home_appbar.dart';
import '../../widgets/prescription_upload_card.dart';
import '../../widgets/ai_ordering_card.dart';
import '../../widgets/refill_reminder_card.dart';
import '../../widgets/custom_bottom_navigation.dart';
import '../../widgets/category_card.dart';
import '../../widgets/offer_card.dart';
import '../profile/profile_screen.dart';
import '../cart/cart_screen.dart';
import '../notifications/notifications_screen.dart';
import '../../services/profile_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;
  late UserModel _user;
  final RefillModel _refill = RefillModel.mock;
  List<Category> _categories = [];
  List<Offer> _offers = [];
  bool _isLoadingCategories = true;
  bool _isLoadingOffers = true;

  @override
  void initState() {
    super.initState();
    _user = ProfileService().getUser();
    ProfileService().addListener(_onProfileUpdated);
    if (_user.name.isEmpty) {
      ProfileService().fetchProfileFromServer();
    }
    _loadHomeData();
  }

  void _onProfileUpdated() {
    if (mounted) {
      setState(() {
        _user = ProfileService().getUser();
      });
    }
  }

  @override
  void dispose() {
    ProfileService().removeListener(_onProfileUpdated);
    super.dispose();
  }

  Future<void> _loadHomeData() async {
    try {
      final categoriesList = await MedicineService.fetchCategories();
      final offersList = await MedicineService.fetchOffers();
      if (mounted) {
        setState(() {
          _categories = categoriesList;
          _offers = offersList;
          _isLoadingCategories = false;
          _isLoadingOffers = false;
        });
      }
    } catch (_) {
      if (mounted) {
        setState(() {
          _isLoadingCategories = false;
          _isLoadingOffers = false;
        });
      }
    }
  }

  void _onItemTapped(int index) {
    if (index == 2) {
      _navigateToChat();
    } else {
      setState(() {
        _selectedIndex = index;
      });
    }
  }

  void _navigateToChat() {
    Navigator.pushNamed(context, AppRoutes.aiChat);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: SafeArea(
        child: _selectedIndex == 0
            ? Column(
                children: [
                  CustomHomeAppBar(user: _user),
                  Expanded(child: _buildHomeBody()),
                ],
              )
            : _buildOtherTabBody(_selectedIndex),
      ),
      bottomNavigationBar: CustomBottomNavigation(
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
      ),
    );
  }

  Widget _buildHomeBody() {
    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(),
      padding: const EdgeInsets.fromLTRB(20, 8, 20, 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Search Medicines Input (Tapping navigates to Search screen)
          FadeSlideTransition(
            delay: const Duration(milliseconds: 50),
            child: GestureDetector(
              onTap: () => Navigator.pushNamed(context, AppRoutes.searchMedicines),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
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
                      blurRadius: 12,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    const Icon(
                      Icons.search_rounded,
                      color: AppTheme.primaryColor,
                      size: 22,
                    ),
                    const SizedBox(width: 12),
                    Text(
                      "Search medicines, dosage, brands...",
                      style: TextStyle(
                        color: AppTheme.textColorSecondary.withOpacity(0.8),
                        fontSize: 14,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const Spacer(),
                    Icon(
                      Icons.mic_none_rounded,
                      color: AppTheme.textColorSecondary.withOpacity(0.6),
                      size: 20,
                    ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(height: 24),

          // Medicine Categories Section
          FadeSlideTransition(
            delay: const Duration(milliseconds: 120),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      "Categories",
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.textColorPrimary,
                        letterSpacing: -0.3,
                      ),
                    ),
                    TextButton(
                      onPressed: () => Navigator.pushNamed(context, AppRoutes.searchMedicines),
                      style: TextButton.styleFrom(
                        padding: EdgeInsets.zero,
                        minimumSize: const Size(0, 0),
                        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        foregroundColor: AppTheme.primaryColor,
                      ),
                      child: const Row(
                        children: [
                          Text(
                            "See All",
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Icon(Icons.keyboard_arrow_right_rounded, size: 16),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                _isLoadingCategories
                    ? _buildCategoriesShimmer()
                    : SizedBox(
                        height: 96,
                        child: ListView.builder(
                          scrollDirection: Axis.horizontal,
                          physics: const BouncingScrollPhysics(),
                          itemCount: _categories.length,
                          itemBuilder: (context, index) {
                            final category = _categories[index];
                            return CategoryCard(
                              category: category,
                              onTap: () {
                                Navigator.pushNamed(
                                  context,
                                  AppRoutes.searchMedicines,
                                  arguments: category.name,
                                );
                              },
                            );
                          },
                        ),
                      ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Quick Actions Section
          FadeSlideTransition(
            delay: const Duration(milliseconds: 140),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  "Quick Actions",
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.textColorPrimary,
                    letterSpacing: -0.3,
                  ),
                ),
                const SizedBox(height: 14),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    _buildQuickActionItem(
                      icon: Icons.file_upload_outlined,
                      label: "Upload Rx",
                      color: AppTheme.primaryColor,
                      onTap: () => Navigator.pushNamed(context, AppRoutes.uploadPrescription),
                    ),
                    _buildQuickActionItem(
                      icon: Icons.auto_awesome_outlined,
                      label: "AI Chat",
                      color: AppTheme.primaryColor,
                      onTap: () => Navigator.pushNamed(context, AppRoutes.aiChat),
                    ),
                    _buildQuickActionItem(
                      icon: Icons.local_shipping_outlined,
                      label: "Track Order",
                      color: AppTheme.primaryColor,
                      onTap: () => Navigator.pushNamed(context, AppRoutes.orderTracking),
                    ),
                    _buildQuickActionItem(
                      icon: Icons.shopping_bag_outlined,
                      label: "My Cart",
                      color: AppTheme.primaryColor,
                      onTap: () => setState(() => _selectedIndex = 3),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 28),

          // Offers Banner Section
          FadeSlideTransition(
            delay: const Duration(milliseconds: 180),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  "Special Offers",
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.textColorPrimary,
                    letterSpacing: -0.3,
                  ),
                ),
                const SizedBox(height: 12),
                _isLoadingOffers
                    ? _buildOffersShimmer()
                    : SizedBox(
                        height: 136,
                        child: ListView.builder(
                          scrollDirection: Axis.horizontal,
                          physics: const BouncingScrollPhysics(),
                          itemCount: _offers.length,
                          itemBuilder: (context, index) {
                            return OfferCard(offer: _offers[index]);
                          },
                        ),
                      ),
              ],
            ),
          ),
          const SizedBox(height: 28),

          // 1. Upload Prescription Card (Staggered Animation 1)
          FadeSlideTransition(
            delay: const Duration(milliseconds: 100),
            child: const PrescriptionUploadCard(),
          ),
          const SizedBox(height: 20),

          // 2. AI Ordering Assistant (Staggered Animation 2)
          FadeSlideTransition(
            delay: const Duration(milliseconds: 250),
            child: const AIOrderingCard(),
          ),
          const SizedBox(height: 20),

          // 3. AI Refill Reminder (Staggered Animation 3)
          FadeSlideTransition(
            delay: const Duration(milliseconds: 400),
            child: RefillReminderCard(
              refill: _refill,
              onReorder: () {
                // Navigate to ordering flow / Chat
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Initiating reorder process for Crocin 650...'),
                    duration: Duration(seconds: 2),
                  ),
                );
                _navigateToChat();
              },
            ),
          ),
          const SizedBox(height: 20),
        ],
      ),
    );
  }

  Widget _buildOtherTabBody(int index) {
    switch (index) {
      case 1:
        return const NotificationsScreen();
      case 3:
        return const CartScreen();
      case 4:
        return const ProfileScreen();
      default:
        return const Center(child: Text("Tab not implemented"));
    }
  }

  // --- Notifications Tab ---
  Widget _buildNotificationsTab() {
    final List<Map<String, String>> notifications = [
      {
        "title": "Refill Alert: Crocin 650",
        "body": "Your Crocin 650 stock is low (estimated 3 days remaining). Reorder now with one tap.",
        "time": "Just Now",
        "type": "refill"
      },
      {
        "title": "Prescription Approved",
        "body": "Your uploaded prescription has been verified by the autonomous pharmacy agent.",
        "time": "2 hours ago",
        "type": "prescription"
      },
      {
        "title": "Order Delivered",
        "body": "Order #ML-9281 containing Vitamins B12 has been delivered successfully.",
        "time": "Yesterday",
        "type": "delivery"
      }
    ];

    return Padding(
      padding: const EdgeInsets.all(20.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            "Notifications",
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: AppTheme.textColorPrimary,
                ),
          ),
          const SizedBox(height: 20),
          Expanded(
            child: ListView.builder(
              physics: const BouncingScrollPhysics(),
              itemCount: notifications.length,
              itemBuilder: (context, index) {
                final item = notifications[index];
                IconData icon;
                Color iconColor;
                switch (item["type"]) {
                  case "refill":
                    icon = Icons.alarm_rounded;
                    iconColor = Colors.orange.shade800;
                    break;
                  case "prescription":
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
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.03),
                        blurRadius: 10,
                        offset: const Offset(0, 4),
                      ),
                    ],
                    border: Border.all(color: Colors.grey.shade100),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: iconColor.withOpacity(0.1),
                          shape: BoxShape.circle,
                        ),
                        child: Icon(icon, color: iconColor, size: 20),
                      ),
                      const SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              item["title"]!,
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 14,
                                color: AppTheme.textColorPrimary,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              item["body"]!,
                              style: TextStyle(
                                color: Colors.grey.shade600,
                                fontSize: 12,
                                height: 1.3,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              item["time"]!,
                              style: TextStyle(
                                color: Colors.grey.shade400,
                                fontSize: 10,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  // --- Cart Tab ---
  Widget _buildCartTab() {
    return Padding(
      padding: const EdgeInsets.all(20.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            "My Cart",
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: AppTheme.textColorPrimary,
                ),
          ),
          const SizedBox(height: 20),
          // Simple item representation
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.03),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
              border: Border.all(color: Colors.grey.shade100),
            ),
            child: Row(
              children: [
                Container(
                  width: 50,
                  height: 50,
                  decoration: BoxDecoration(
                    color: AppTheme.primaryColor.withOpacity(0.08),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(
                    Icons.medication_rounded,
                    color: AppTheme.primaryColor,
                  ),
                ),
                const SizedBox(width: 14),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        "Crocin 650",
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 15,
                          color: AppTheme.textColorPrimary,
                        ),
                      ),
                      SizedBox(height: 4),
                      Text(
                        "Tablet • 15 Units",
                        style: TextStyle(
                          color: Colors.grey,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
                const Text(
                  "₹35.0",
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                    color: AppTheme.primaryColor,
                  ),
                ),
              ],
            ),
          ),
          const Spacer(),
          // Order Details Summary
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: AppTheme.cardColor,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              children: [
                _buildSummaryRow("Item Subtotal", "₹35.0"),
                const SizedBox(height: 8),
                _buildSummaryRow("Delivery Charges", "₹0.0 (Free)"),
                const Divider(height: 24),
                _buildSummaryRow("Total Amount", "₹35.0", isTotal: true),
              ],
            ),
          ),
          const SizedBox(height: 20),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Processing checkout... Autopilot pharmacy agent engaged.'),
                  ),
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.primaryColor,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
              ),
              child: const Text(
                "Proceed to Checkout",
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
            ),
          ),
          const SizedBox(height: 8),
        ],
      ),
    );
  }

  Widget _buildSummaryRow(String label, String value, {bool isTotal = false}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: TextStyle(
            fontWeight: isTotal ? FontWeight.bold : FontWeight.normal,
            fontSize: isTotal ? 16 : 14,
            color: isTotal ? AppTheme.textColorPrimary : Colors.grey.shade600,
          ),
        ),
        Text(
          value,
          style: TextStyle(
            fontWeight: isTotal ? FontWeight.bold : FontWeight.w600,
            fontSize: isTotal ? 18 : 14,
            color: isTotal ? AppTheme.primaryColor : AppTheme.textColorPrimary,
          ),
        ),
      ],
    );
  }

  // --- Profile Tab ---
  Widget _buildProfileTab() {
    return const ProfileScreen();
  }

  Widget _buildCategoriesShimmer() {
    return SizedBox(
      height: 96,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: 5,
        itemBuilder: (context, index) {
          return Container(
            width: 84,
            margin: const EdgeInsets.only(right: 12),
            child: Column(
              children: [
                Container(
                  height: 64,
                  width: 64,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade100,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(height: 8),
                Container(
                  height: 12,
                  width: 45,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildOffersShimmer() {
    return SizedBox(
      height: 136,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: 2,
        itemBuilder: (context, index) {
          return Container(
            width: 290,
            margin: const EdgeInsets.only(right: 16),
            decoration: BoxDecoration(
              color: Colors.grey.shade100,
              borderRadius: BorderRadius.circular(24),
            ),
          );
        },
      ),
    );
  }

  Widget _buildQuickActionItem({
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          margin: const EdgeInsets.symmetric(horizontal: 4),
          padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 8),
          decoration: BoxDecoration(
            color: AppTheme.cardColor,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: const Color(0xFFE5E7EB).withOpacity(0.5),
              width: 1,
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.015),
                blurRadius: 8,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: AppTheme.secondaryColor.withOpacity(0.4),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  icon,
                  color: AppTheme.primaryColor,
                  size: 22,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                label,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  color: AppTheme.textColorPrimary,
                  letterSpacing: -0.1,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// --- Fade Slide Transition Helper Widget ---
class FadeSlideTransition extends StatefulWidget {
  final Widget child;
  final Duration delay;

  const FadeSlideTransition({
    super.key,
    required this.child,
    required this.delay,
  });

  @override
  State<FadeSlideTransition> createState() => _FadeSlideTransitionState();
}

class _FadeSlideTransitionState extends State<FadeSlideTransition>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _opacityAnimation;
  late Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 700),
    );

    _opacityAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.0, 0.6, curve: Curves.easeOut),
      ),
    );

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0.0, 0.12),
      end: Offset.zero,
    ).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.0, 1.0, curve: Curves.easeOutCubic),
      ),
    );

    Future.delayed(widget.delay, () {
      if (mounted) {
        _controller.forward();
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SlideTransition(
      position: _slideAnimation,
      child: FadeTransition(
        opacity: _opacityAnimation,
        child: widget.child,
      ),
    );
  }
}
