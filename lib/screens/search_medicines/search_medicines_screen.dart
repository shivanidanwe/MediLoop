import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../models/medicine_model.dart';
import '../../services/medicine_service.dart';
import '../../routes/app_routes.dart';

class SearchMedicinesScreen extends StatefulWidget {
  const SearchMedicinesScreen({super.key});

  @override
  State<SearchMedicinesScreen> createState() => _SearchMedicinesScreenState();
}

class _SearchMedicinesScreenState extends State<SearchMedicinesScreen> {
  final TextEditingController _searchController = TextEditingController();
  List<Medicine> _searchResults = [];
  bool _isLoading = false;
  String _selectedDosageFilter = "All"; // "All", "Tablet", "Capsule", "Syrup"
  bool? _requirePrescriptionFilter; // null: All, true: Yes, false: No

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _onSearchChanged(String query) async {
    if (query.trim().isEmpty) {
      setState(() {
        _searchResults = [];
        _isLoading = false;
      });
      return;
    }

    setState(() {
      _isLoading = true;
    });

    // Simulated API call
    final results = await MedicineService.searchMedicines(query);
    
    if (mounted) {
      setState(() {
        _searchResults = results;
        _isLoading = false;
      });
    }
  }

  void _simulateVoiceSearch() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        // Close voice search after 2.5 seconds and fill in "Dolo 650"
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
              // Pulsing mic icon
              TweenAnimationBuilder<double>(
                tween: Tween(begin: 1.0, end: 1.3),
                duration: const Duration(seconds: 1),
                curve: Curves.easeInOut,
                onEnd: () {},
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

  // Filter application
  List<Medicine> _getFilteredResults() {
    return _searchResults.where((med) {
      // Apply dosage filter
      if (_selectedDosageFilter != "All" && med.dosageForm.toLowerCase() != _selectedDosageFilter.toLowerCase()) {
        return false;
      }
      // Apply prescription filter
      if (_requirePrescriptionFilter != null && med.prescriptionRequired != _requirePrescriptionFilter) {
        return false;
      }
      return true;
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    final filteredMedicines = _getFilteredResults();

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text("Search Medicines", style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
      ),
      body: SafeArea(
        child: Column(
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
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
      child: Row(
        children: [
          // Dosage Forms Filters
          _buildFilterChip("All Forms", _selectedDosageFilter == "All", () {
            setState(() => _selectedDosageFilter = "All");
          }),
          _buildFilterChip("Tablets", _selectedDosageFilter == "Tablet", () {
            setState(() => _selectedDosageFilter = "Tablet");
          }),
          _buildFilterChip("Syrups", _selectedDosageFilter == "Syrup", () {
            setState(() => _selectedDosageFilter = "Syrup");
          }),
          _buildFilterChip("Capsules", _selectedDosageFilter == "Capsule", () {
            setState(() => _selectedDosageFilter = "Capsule");
          }),

          const SizedBox(width: 12),
          Container(height: 24, width: 1, color: Colors.grey.shade300),
          const SizedBox(width: 12),

          // Prescription Requirement Filters
          _buildFilterChip("Prescription Not Required", _requirePrescriptionFilter == false, () {
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
          color: isSelected ? AppTheme.primaryColor : Colors.grey.shade600,
          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
          fontSize: 12,
        ),
        backgroundColor: Colors.white,
        side: BorderSide(color: isSelected ? AppTheme.primaryColor : Colors.grey.shade200),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );
  }

  Widget _buildShimmerLoading() {
    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      itemCount: 4,
      itemBuilder: (context, index) {
        return Container(
          margin: const EdgeInsets.only(bottom: 16),
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
                  borderRadius: BorderRadius.circular(10),
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
    final hasSearch = _searchController.text.isNotEmpty;
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 40.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              hasSearch ? Icons.search_off_rounded : Icons.search_rounded,
              size: 80,
              color: Colors.grey.shade300,
            ),
            const SizedBox(height: 20),
            Text(
              hasSearch ? "No Medicines Found" : "Find Your Medicine",
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: AppTheme.textColorPrimary),
            ),
            const SizedBox(height: 8),
            Text(
              hasSearch
                  ? "We couldn't find any medicine matching '${_searchController.text}'. Try searching for generic compounds or check spelling."
                  : "Type medicine name, manufacturer, or treatment symptoms in the search bar above.",
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey.shade500, fontSize: 13, height: 1.4),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildResultsList(List<Medicine> medicines) {
    return ListView.builder(
      physics: const BouncingScrollPhysics(),
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
      itemCount: medicines.length,
      itemBuilder: (context, index) {
        final med = medicines[index];
        IconData dosageIcon;
        switch (med.dosageForm.toLowerCase()) {
          case 'tablet':
            dosageIcon = Icons.tablet_rounded;
            break;
          case 'syrup':
            dosageIcon = Icons.medication_liquid;
            break;
          default:
            dosageIcon = Icons.medication_rounded;
        }

        return Container(
          margin: const EdgeInsets.only(bottom: 16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.02),
                blurRadius: 10,
                offset: const Offset(0, 4),
              ),
            ],
            border: Border.all(color: Colors.grey.shade100),
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
              borderRadius: BorderRadius.circular(16),
              child: Padding(
                padding: const EdgeInsets.all(12.0),
                child: Row(
                  children: [
                    // Medicine Icon Box
                    Container(
                      width: 80,
                      height: 80,
                      decoration: BoxDecoration(
                        color: AppTheme.primaryColor.withOpacity(0.08),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Icon(
                        dosageIcon,
                        color: AppTheme.primaryColor,
                        size: 36,
                      ),
                    ),
                    const SizedBox(width: 16),

                    // Info Column
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Expanded(
                                child: Text(
                                  med.name,
                                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: AppTheme.textColorPrimary),
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                              if (med.prescriptionRequired)
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: Colors.red.shade50,
                                    borderRadius: BorderRadius.circular(6),
                                    border: Border.all(color: Colors.red.shade100, width: 0.5),
                                  ),
                                  child: const Text(
                                    "Rx Required",
                                    style: TextStyle(color: Colors.red, fontSize: 9, fontWeight: FontWeight.bold),
                                  ),
                                ),
                            ],
                          ),
                          const SizedBox(height: 4),
                          Text(
                            "${med.dosageForm} • ${med.strength}",
                            style: TextStyle(color: Colors.grey.shade500, fontSize: 12),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            med.manufacturer,
                            style: TextStyle(color: Colors.grey.shade400, fontSize: 11),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                          const SizedBox(height: 8),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                "₹${med.price.toStringAsFixed(2)}",
                                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: AppTheme.primaryColor),
                              ),
                              Row(
                                children: [
                                  const Icon(Icons.star_rounded, color: Colors.amber, size: 14),
                                  const SizedBox(width: 2),
                                  Text(
                                    med.rating.toString(),
                                    style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppTheme.textColorPrimary),
                                  ),
                                ],
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
