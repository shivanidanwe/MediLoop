import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../models/medicine_model.dart';
import '../../services/medicine_service.dart';
import '../../services/cart_service.dart';
import '../../routes/app_routes.dart';

class SearchMedicinesScreen extends StatefulWidget {
  const SearchMedicinesScreen({super.key});

  @override
  State<SearchMedicinesScreen> createState() => _SearchMedicinesScreenState();
}

class _SearchMedicinesScreenState extends State<SearchMedicinesScreen> {
  final TextEditingController _searchController = TextEditingController();
  List<Medicine> _allMedicines = [];
  bool _isLoading = true;
  String _selectedDosageFilter = "All"; // "All", "Tablet", "Capsule", "Syrup"
  bool? _requirePrescriptionFilter; // null: All, true: Yes, false: No

  @override
  void initState() {
    super.initState();
    _loadAllMedicines();

    WidgetsBinding.instance.addPostFrameCallback((_) {
      final args = ModalRoute.of(context)?.settings.arguments;
      if (args is String && args.isNotEmpty) {
        final lower = args.toLowerCase();
        if (lower.contains('tablet')) {
          setState(() => _selectedDosageFilter = "Tablet");
        } else if (lower.contains('syrup')) {
          setState(() => _selectedDosageFilter = "Syrup");
        } else if (lower.contains('capsule')) {
          setState(() => _selectedDosageFilter = "Capsule");
        } else {
          _searchController.text = args;
        }
      }
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadAllMedicines() async {
    setState(() => _isLoading = true);
    final medicines = await MedicineService.fetchMedicines(limit: 60);
    if (mounted) {
      setState(() {
        _allMedicines = medicines;
        _isLoading = false;
      });
    }
  }

  void _onSearchChanged(String query) {
    setState(() {});
  }

  void _resetFilters() {
    setState(() {
      _searchController.clear();
      _selectedDosageFilter = "All";
      _requirePrescriptionFilter = null;
    });
  }

  void _simulateVoiceSearch() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        Future.delayed(const Duration(milliseconds: 2000), () {
          if (Navigator.canPop(context)) {
            Navigator.pop(context);
            _searchController.text = "Dolo 650";
            _onSearchChanged("Dolo 650");
          }
        });

        return Container(
          padding: const EdgeInsets.symmetric(vertical: 40, horizontal: 24),
          decoration: const BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                "Listening...",
                style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 32),
              TweenAnimationBuilder<double>(
                tween: Tween(begin: 1.0, end: 1.3),
                duration: const Duration(seconds: 1),
                curve: Curves.easeInOut,
                builder: (context, scale, child) {
                  return Transform.scale(
                    scale: scale,
                    child: Container(
                      padding: const EdgeInsets.all(24),
                      decoration: BoxDecoration(
                        color: AppTheme.primaryColor.withOpacity(0.1),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.mic_none_rounded,
                        size: 48,
                        color: AppTheme.primaryColor,
                      ),
                    ),
                  );
                },
              ),
              const SizedBox(height: 32),
              Text(
                "Try saying 'Dolo 650' or 'Cough Syrup'",
                style: TextStyle(color: Colors.grey.shade500, fontSize: 13),
              ),
            ],
          ),
        );
      },
    );
  }

  // Filter application - always filters from all medicines so screen is never blank!
  List<Medicine> _getFilteredResults() {
    final query = _searchController.text.trim().toLowerCase();

    return _allMedicines.where((med) {
      if (query.isNotEmpty) {
        final nameMatch = med.name.toLowerCase().contains(query);
        final descMatch = med.description.toLowerCase().contains(query);
        final mfgMatch = med.manufacturer.toLowerCase().contains(query);
        final strengthMatch = med.strength.toLowerCase().contains(query);
        final formMatch = med.dosageForm.toLowerCase().contains(query);

        if (!nameMatch && !descMatch && !mfgMatch && !strengthMatch && !formMatch) {
          return false;
        }
      }

      // Apply dosage form filter
      if (_selectedDosageFilter != "All" &&
          med.dosageForm.toLowerCase() != _selectedDosageFilter.toLowerCase()) {
        return false;
      }

      // Apply prescription requirement filter
      if (_requirePrescriptionFilter != null &&
          med.prescriptionRequired != _requirePrescriptionFilter) {
        return false;
      }

      return true;
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    final filteredMedicines = _getFilteredResults();
    final isSearching = _searchController.text.trim().isNotEmpty;
    final hasActiveFilter = _selectedDosageFilter != "All" || _requirePrescriptionFilter != null;

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text("Search Medicines", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: AppTheme.textColorPrimary)),
        backgroundColor: Colors.white,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 18, color: AppTheme.textColorPrimary),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.shopping_bag_outlined, color: AppTheme.textColorPrimary),
            onPressed: () => Navigator.pushNamed(context, AppRoutes.cart),
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Search Input Row
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 8.0),
              child: Row(
                children: [
                  Expanded(
                    child: Container(
                      decoration: BoxDecoration(
                        color: AppTheme.cardColor,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: Colors.grey.shade200),
                      ),
                      child: TextField(
                        controller: _searchController,
                        onChanged: _onSearchChanged,
                        decoration: InputDecoration(
                          hintText: "Search name, dosage, symptoms...",
                          hintStyle: TextStyle(color: Colors.grey.shade400, fontSize: 14),
                          prefixIcon: const Icon(Icons.search_rounded, color: AppTheme.primaryColor),
                          suffixIcon: _searchController.text.isNotEmpty
                              ? IconButton(
                                  icon: const Icon(Icons.clear_rounded, color: Colors.grey),
                                  onPressed: () {
                                    _searchController.clear();
                                    _onSearchChanged("");
                                  },
                                )
                              : null,
                          border: InputBorder.none,
                          enabledBorder: InputBorder.none,
                          focusedBorder: InputBorder.none,
                          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  CircleAvatar(
                    radius: 26,
                    backgroundColor: AppTheme.primaryColor.withOpacity(0.1),
                    child: IconButton(
                      icon: const Icon(Icons.mic_rounded, color: AppTheme.primaryColor),
                      onPressed: _simulateVoiceSearch,
                    ),
                  ),
                ],
              ),
            ),

            // Filter Chips
            _buildFiltersRow(),

            // Status Bar showing item count & active filters
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 4, 20, 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(
                      isSearching
                          ? "Results for '${_searchController.text.trim()}' (${filteredMedicines.length})"
                          : hasActiveFilter
                              ? "Filtered Medicines (${filteredMedicines.length})"
                              : "All Catalog Medicines (${filteredMedicines.length})",
                      style: const TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.textColorSecondary,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  if (isSearching || hasActiveFilter)
                    TextButton(
                      onPressed: _resetFilters,
                      style: TextButton.styleFrom(
                        padding: EdgeInsets.zero,
                        minimumSize: const Size(0, 0),
                        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      ),
                      child: const Text("Clear All", style: TextStyle(fontSize: 12, color: AppTheme.primaryColor, fontWeight: FontWeight.bold)),
                    ),
                ],
              ),
            ),

            // List or Empty/Loading State
            Expanded(
              child: _isLoading
                  ? _buildShimmerLoading()
                  : filteredMedicines.isEmpty
                      ? _buildEmptyState()
                      : _buildResultsList(filteredMedicines),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFiltersRow() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      physics: const BouncingScrollPhysics(),
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 6),
      child: Row(
        children: [
          // Dosage Forms Filters
          _buildFilterChip("All Forms", _selectedDosageFilter == "All", () {
            setState(() => _selectedDosageFilter = "All");
          }),
          _buildFilterChip("Tablets", _selectedDosageFilter == "Tablet", () {
            setState(() => _selectedDosageFilter = _selectedDosageFilter == "Tablet" ? "All" : "Tablet");
          }),
          _buildFilterChip("Syrups", _selectedDosageFilter == "Syrup", () {
            setState(() => _selectedDosageFilter = _selectedDosageFilter == "Syrup" ? "All" : "Syrup");
          }),
          _buildFilterChip("Capsules", _selectedDosageFilter == "Capsule", () {
            setState(() => _selectedDosageFilter = _selectedDosageFilter == "Capsule" ? "All" : "Capsule");
          }),

          const SizedBox(width: 8),
          Container(height: 20, width: 1, color: Colors.grey.shade300),
          const SizedBox(width: 8),

          // Prescription Requirement Filters
          _buildFilterChip("OTC / No Rx", _requirePrescriptionFilter == false, () {
            setState(() {
              _requirePrescriptionFilter = _requirePrescriptionFilter == false ? null : false;
            });
          }),
          _buildFilterChip("Prescription Required 📄", _requirePrescriptionFilter == true, () {
            setState(() {
              _requirePrescriptionFilter = _requirePrescriptionFilter == true ? null : true;
            });
          }),
        ],
      ),
    );
  }

  Widget _buildFilterChip(String label, bool isSelected, VoidCallback onTap) {
    return Padding(
      padding: const EdgeInsets.only(right: 8.0),
      child: ChoiceChip(
        label: Text(label),
        selected: isSelected,
        onSelected: (_) => onTap(),
        selectedColor: AppTheme.primaryColor.withOpacity(0.12),
        checkmarkColor: AppTheme.primaryColor,
        labelStyle: TextStyle(
          color: isSelected ? AppTheme.primaryColor : Colors.grey.shade700,
          fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
          fontSize: 12,
        ),
        backgroundColor: Colors.white,
        side: BorderSide(color: isSelected ? AppTheme.primaryColor : Colors.grey.shade300),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );
  }

  Widget _buildShimmerLoading() {
    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      itemCount: 5,
      itemBuilder: (context, index) {
        return Container(
          margin: const EdgeInsets.only(bottom: 14),
          height: 100,
          decoration: BoxDecoration(
            color: Colors.grey.shade50,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.grey.shade100),
          ),
          child: Row(
            children: [
              Container(
                margin: const EdgeInsets.all(12),
                width: 76,
                decoration: BoxDecoration(
                  color: Colors.grey.shade200,
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Container(height: 16, width: 140, color: Colors.grey.shade200),
                      Container(height: 12, width: 80, color: Colors.grey.shade200),
                      Container(height: 14, width: 50, color: Colors.grey.shade200),
                    ],
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 40.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.search_off_rounded,
              size: 68,
              color: Colors.grey.shade300,
            ),
            const SizedBox(height: 16),
            const Text(
              "No Matching Medicines Found",
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: AppTheme.textColorPrimary),
            ),
            const SizedBox(height: 8),
            Text(
              "No medicines found matching your search or filters. Try relaxing your filters or check the medicine spelling.",
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey.shade600, fontSize: 13, height: 1.4),
            ),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              onPressed: _resetFilters,
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.primaryColor,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
              ),
              icon: const Icon(Icons.refresh_rounded, size: 16, color: Colors.white),
              label: const Text("Show All Medicines", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildResultsList(List<Medicine> medicines) {
    return ListView.builder(
      physics: const BouncingScrollPhysics(),
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 6),
      itemCount: medicines.length,
      itemBuilder: (context, index) {
        final med = medicines[index];
        IconData dosageIcon;
        Color iconBgColor;
        switch (med.dosageForm.toLowerCase()) {
          case 'tablet':
            dosageIcon = Icons.tablet_rounded;
            iconBgColor = const Color(0xFFE8F5E9);
            break;
          case 'syrup':
            dosageIcon = Icons.medication_liquid_rounded;
            iconBgColor = const Color(0xFFFFF3E0);
            break;
          case 'capsule':
            dosageIcon = Icons.medication_rounded;
            iconBgColor = const Color(0xFFE0F7FA);
            break;
          case 'inhaler':
            dosageIcon = Icons.air_rounded;
            iconBgColor = const Color(0xFFEDE7F6);
            break;
          default:
            dosageIcon = Icons.medical_services_rounded;
            iconBgColor = const Color(0xFFF1F8E9);
        }

        return Container(
          margin: const EdgeInsets.only(bottom: 14),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.02),
                blurRadius: 10,
                offset: const Offset(0, 4),
              ),
            ],
            border: Border.all(color: const Color(0xFFE5E7EB).withOpacity(0.6)),
          ),
          child: Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: () {
                Navigator.pushNamed(
                  context,
                  AppRoutes.medicineDetails,
                  arguments: med,
                );
              },
              borderRadius: BorderRadius.circular(20),
              child: Padding(
                padding: const EdgeInsets.all(14.0),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Medicine Image or Styled Graphic Tile
                    Container(
                      width: 72,
                      height: 72,
                      decoration: BoxDecoration(
                        color: iconBgColor,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: Colors.black.withOpacity(0.04)),
                      ),
                      child: (med.imageUrl.isNotEmpty && med.imageUrl.startsWith('http'))
                          ? ClipRRect(
                              borderRadius: BorderRadius.circular(16),
                              child: Image.network(
                                med.imageUrl,
                                fit: BoxFit.cover,
                                errorBuilder: (_, __, ___) => Icon(dosageIcon, color: AppTheme.primaryColor, size: 32),
                              ),
                            )
                          : Icon(
                              dosageIcon,
                              color: AppTheme.primaryColor,
                              size: 32,
                            ),
                    ),
                    const SizedBox(width: 14),

                    // Info Column
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Expanded(
                                child: Text(
                                  med.name,
                                  style: const TextStyle(
                                    fontWeight: FontWeight.bold,
                                    fontSize: 15.5,
                                    color: AppTheme.textColorPrimary,
                                    letterSpacing: -0.2,
                                  ),
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                              const SizedBox(width: 6),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2.5),
                                decoration: BoxDecoration(
                                  color: med.prescriptionRequired
                                      ? Colors.red.shade50
                                      : const Color(0xFF2E7D32).withOpacity(0.1),
                                  borderRadius: BorderRadius.circular(6),
                                  border: Border.all(
                                    color: med.prescriptionRequired ? Colors.red.shade100 : const Color(0xFF2E7D32).withOpacity(0.2),
                                    width: 0.5,
                                  ),
                                ),
                                child: Text(
                                  med.prescriptionRequired ? "Rx Required" : "OTC",
                                  style: TextStyle(
                                    color: med.prescriptionRequired ? Colors.red.shade800 : const Color(0xFF2E7D32),
                                    fontSize: 9.5,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 3),
                          Text(
                            "${med.dosageForm} • ${med.strength}",
                            style: const TextStyle(color: AppTheme.textColorSecondary, fontSize: 12, fontWeight: FontWeight.w500),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            med.manufacturer,
                            style: TextStyle(color: Colors.grey.shade400, fontSize: 11),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                          const SizedBox(height: 10),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                "₹${med.price.toStringAsFixed(2)}",
                                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16.5, color: AppTheme.primaryColor),
                              ),
                              // Add to Cart Button
                              ElevatedButton.icon(
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: AppTheme.primaryColor,
                                  foregroundColor: Colors.white,
                                  elevation: 0,
                                  minimumSize: Size.zero,
                                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                                ),
                                onPressed: () {
                                  CartService().addItem(med);
                                  ScaffoldMessenger.of(context).hideCurrentSnackBar();
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(
                                      content: Text("Added ${med.name} to Cart"),
                                      duration: const Duration(seconds: 2),
                                      backgroundColor: AppTheme.primaryColor,
                                      action: SnackBarAction(
                                        label: "View Cart",
                                        textColor: Colors.white,
                                        onPressed: () => Navigator.pushNamed(context, AppRoutes.cart),
                                      ),
                                    ),
                                  );
                                },
                                icon: const Icon(Icons.add_shopping_cart_rounded, size: 14),
                                label: const Text("Add", style: TextStyle(fontSize: 11.5, fontWeight: FontWeight.bold)),
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
        );
      },
    );
  }
}
