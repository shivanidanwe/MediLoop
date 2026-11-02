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
import '../../widgets/liquid_glass_card.dart';
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
  RefillModel _refill = RefillModel(
    medicineName: "Prescribed Medicine",
    daysRemaining: 4,
    percentageRemaining: 0.65,
  );
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
      final recentOrders = await MedicineService.fetchRecentOrders();

      if (mounted) {
        setState(() {
          _categories = categoriesList;
          _offers = offersList;
          if (recentOrders.isNotEmpty) {
            _refill = RefillModel(
              medicineName: recentOrders.first.medicineName,
              daysRemaining: 4,
              percentageRemaining: 0.60,
            );
          }
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
    return PopScope(
      canPop: _selectedIndex == 0,
      onPopInvokedWithResult: (didPop, _) {
        if (!didPop && _selectedIndex != 0) {
          setState(() {
            _selectedIndex = 0;
          });
        }
      },
      child: Scaffold(
        backgroundColor: AppTheme.cloudWhite,
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
      ),
    );
  }

  Widget _buildHomeBody() {
    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(),
      padding: const EdgeInsets.fromLTRB(20, 4, 20, 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 1. Sleek Liquid Glass Search Input
          FadeSlideTransition(
            delay: const Duration(milliseconds: 50),
            child: GestureDetector(
              onTap: () => Navigator.pushNamed(context, AppRoutes.searchMedicines),
              child: LiquidGlassCard(
                borderRadius: 20,
                padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
                child: Row(
                  children: [
                    const Icon(
                      Icons.search_rounded,
                      color: AppTheme.royalBlue,
                      size: 22,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        "Search medicines, dosages, generics...",
                        style: TextStyle(
                          color: AppTheme.textColorSecondary.withOpacity(0.8),
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.all(6),
                      decoration: BoxDecoration(
                        color: AppTheme.royalBlue.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: const Icon(
                        Icons.mic_none_rounded,
                        color: AppTheme.royalBlue,
                        size: 18,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(height: 20),

          // 2. Large Colorful Hero Card ("Your Health. Our Priority.")
          FadeSlideTransition(
            delay: const Duration(milliseconds: 90),
            child: Container(
              width: double.infinity,
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [
                    AppTheme.midnightNavy,
                    AppTheme.deepBlue,
                    AppTheme.royalBlue,
                  ],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(26),
                border: Border.all(
                  color: Colors.white.withOpacity(0.25),
                  width: 1.5,
                ),
                boxShadow: [
                  BoxShadow(
                    color: AppTheme.royalBlue.withOpacity(0.28),
                    blurRadius: 28,
                    offset: const Offset(0, 10),
                  ),
                ],
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(26),
                child: Stack(
                  children: [
                    // Decorative ambient light
                    Positioned(
                      right: -30,
                      top: -30,
                      child: Container(
                        width: 160,
                        height: 160,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          gradient: RadialGradient(
                            colors: [
                              AppTheme.electricCyan.withOpacity(0.4),
                              Colors.transparent,
                            ],
                          ),
                        ),
                      ),
                    ),
                    Positioned(
                      left: -20,
                      bottom: -20,
                      child: Container(
                        width: 140,
                        height: 140,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          gradient: RadialGradient(
                            colors: [
                              AppTheme.violet.withOpacity(0.3),
                              Colors.transparent,
                            ],
                          ),
                        ),
                      ),
                    ),

                    Padding(
                      padding: const EdgeInsets.all(24.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                decoration: BoxDecoration(
                                  color: Colors.white.withOpacity(0.15),
                                  borderRadius: BorderRadius.circular(10),
                                  border: Border.all(color: Colors.white.withOpacity(0.3)),
                                ),
                                child: const Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Icon(Icons.shield_outlined, color: AppTheme.mint, size: 14),
                                    SizedBox(width: 5),
                                    Text(
                                      "SMART HEALTHCARE",
                                      style: TextStyle(
                                        color: AppTheme.mint,
                                        fontSize: 10,
                                        fontWeight: FontWeight.w800,
                                        letterSpacing: 0.8,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              const Spacer(),
                              const Icon(Icons.all_inclusive_rounded, color: AppTheme.electricCyan, size: 28),
                            ],
                          ),
                          const SizedBox(height: 16),
                          const Text(
                            "Your Health.\nOur Priority.",
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 26,
                              fontWeight: FontWeight.w900,
                              height: 1.15,
                              letterSpacing: -0.6,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            "Autonomous prescription verification, verified genuine medicines, and rapid doorstep delivery.",
                            style: TextStyle(
                              color: Colors.white.withOpacity(0.85),
                              fontSize: 13,
                              height: 1.4,
                            ),
                          ),
                          const SizedBox(height: 20),
                          Row(
                            children: [
                              GestureDetector(
                                onTap: () => Navigator.pushNamed(context, AppRoutes.uploadPrescription),
                                child: Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 10),
                                  decoration: BoxDecoration(
                                    gradient: const LinearGradient(
                                      colors: [AppTheme.electricCyan, AppTheme.aqua],
                                      begin: Alignment.topLeft,
                                      end: Alignment.bottomRight,
                                    ),
                                    borderRadius: BorderRadius.circular(14),
                                    boxShadow: [
                                      BoxShadow(
                                        color: AppTheme.electricCyan.withOpacity(0.35),
                                        blurRadius: 14,
                                        offset: const Offset(0, 4),
                                      ),
                                    ],
                                  ),
                                  child: const Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Icon(Icons.cloud_upload_outlined, color: AppTheme.midnightNavy, size: 18),
                                      SizedBox(width: 8),
                                      Text(
                                        "Upload Rx",
                                        style: TextStyle(
                                          color: AppTheme.midnightNavy,
                                          fontWeight: FontWeight.w800,
                                          fontSize: 13,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                              const SizedBox(width: 12),
                              GestureDetector(
                                onTap: () => Navigator.pushNamed(context, AppRoutes.searchMedicines),
                                child: Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                                  decoration: BoxDecoration(
                                    color: Colors.white.withOpacity(0.12),
                                    borderRadius: BorderRadius.circular(14),
                                    border: Border.all(color: Colors.white.withOpacity(0.25)),
                                  ),
                                  child: const Text(
                                    "Browse Catalog",
                                    style: TextStyle(
                                      color: Colors.white,
                                      fontWeight: FontWeight.w700,
                                      fontSize: 13,
                                    ),
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
              ),
            ),
          ),
          const SizedBox(height: 24),

          // 3. Quick Action Grid (Upload Rx, Buy Medicines, Track Order, AI Assistant)
          FadeSlideTransition(
            delay: const Duration(milliseconds: 130),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  "Quick Care Actions",
                  style: TextStyle(
                    fontSize: 17,
                    fontWeight: FontWeight.w800,
                    color: AppTheme.midnightNavy,
                    letterSpacing: -0.3,
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    _buildQuickActionItem(
                      icon: Icons.receipt_long_rounded,
                      label: "Upload Rx",
                      gradient: const LinearGradient(colors: [AppTheme.royalBlue, AppTheme.electricCyan]),
                      onTap: () => Navigator.pushNamed(context, AppRoutes.uploadPrescription),
                    ),
                    _buildQuickActionItem(
                      icon: Icons.medication_liquid_rounded,
                      label: "Buy Meds",
                      gradient: const LinearGradient(colors: [AppTheme.violet, AppTheme.lavender]),
                      onTap: () => Navigator.pushNamed(context, AppRoutes.searchMedicines),
                    ),
                    _buildQuickActionItem(
                      icon: Icons.local_shipping_rounded,
                      label: "Track Order",
                      gradient: const LinearGradient(colors: [AppTheme.electricCyan, AppTheme.aqua]),
                      onTap: () => Navigator.pushNamed(context, AppRoutes.orderTracking),
                    ),
                    _buildQuickActionItem(
                      icon: Icons.auto_awesome_rounded,
                      label: "AI Chat",
                      gradient: const LinearGradient(colors: [AppTheme.softPink, AppTheme.warmYellow]),
                      onTap: () => Navigator.pushNamed(context, AppRoutes.aiChat),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // 4. Medicine Categories Section
          FadeSlideTransition(
            delay: const Duration(milliseconds: 160),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      "Healthcare Categories",
                      style: TextStyle(
                        fontSize: 17,
                        fontWeight: FontWeight.w800,
                        color: AppTheme.midnightNavy,
                        letterSpacing: -0.3,
                      ),
                    ),
                    GestureDetector(
                      onTap: () => Navigator.pushNamed(context, AppRoutes.searchMedicines),
                      child: const Row(
                        children: [
                          Text(
                            "See All",
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w700,
                              color: AppTheme.royalBlue,
                            ),
                          ),
                          Icon(Icons.keyboard_arrow_right_rounded, size: 16, color: AppTheme.royalBlue),
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

          // 5. Special Promotional Offers
          FadeSlideTransition(
            delay: const Duration(milliseconds: 190),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  "Exclusive Health Deals",
                  style: TextStyle(
                    fontSize: 17,
                    fontWeight: FontWeight.w800,
                    color: AppTheme.midnightNavy,
                    letterSpacing: -0.3,
                  ),
                ),
                const SizedBox(height: 12),
                _isLoadingOffers
                    ? _buildOffersShimmer()
                    : SizedBox(
                        height: 140,
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
          const SizedBox(height: 24),

          // 6. Upload Prescription Card
          const FadeSlideTransition(
            delay: Duration(milliseconds: 220),
            child: PrescriptionUploadCard(),
          ),
          const SizedBox(height: 18),

          // 7. AI Ordering Assistant Card
          const FadeSlideTransition(
            delay: Duration(milliseconds: 260),
            child: AIOrderingCard(),
          ),
          const SizedBox(height: 18),

          // 8. AI Refill Reminder Card
          FadeSlideTransition(
            delay: const Duration(milliseconds: 300),
            child: RefillReminderCard(
              refill: _refill,
              onReorder: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: const Text('Initiating reorder process for medication...'),
                    backgroundColor: AppTheme.royalBlue,
                    behavior: SnackBarBehavior.floating,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
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
        return ProfileScreen(
          onBackToHome: () {
            setState(() {
              _selectedIndex = 0;
            });
          },
        );
      default:
        return const Center(child: Text("Tab not implemented"));
    }
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
            width: 82,
            margin: const EdgeInsets.only(right: 12),
            child: Column(
              children: [
                Container(
                  height: 60,
                  width: 60,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(20),
                  ),
                ),
                const SizedBox(height: 8),
                Container(
                  height: 10,
                  width: 44,
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
      height: 140,
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
    required Gradient gradient,
    required VoidCallback onTap,
  }) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          margin: const EdgeInsets.symmetric(horizontal: 4),
          padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 6),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(18),
            border: Border.all(
              color: Colors.grey.shade200,
              width: 1.2,
            ),
            boxShadow: [
              BoxShadow(
                color: AppTheme.midnightNavy.withOpacity(0.03),
                blurRadius: 10,
                offset: const Offset(0, 3),
              ),
            ],
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 42,
                height: 42,
                decoration: BoxDecoration(
                  gradient: gradient,
                  borderRadius: BorderRadius.circular(14),
                  boxShadow: [
                    BoxShadow(
                      color: AppTheme.royalBlue.withOpacity(0.2),
                      blurRadius: 8,
                      offset: const Offset(0, 3),
                    ),
                  ],
                ),
                child: Center(
                  child: Icon(icon, color: Colors.white, size: 20),
                ),
              ),
              const SizedBox(height: 8),
              Text(
                label,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                  color: AppTheme.midnightNavy,
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
