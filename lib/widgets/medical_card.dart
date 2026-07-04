import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import '../models/user_model.dart';

class MedicalCard extends StatefulWidget {
  final UserModel user;
  final Function(List<String> conditions, String allergies) onSave;

  const MedicalCard({
    super.key,
    required this.user,
    required this.onSave,
  });

  @override
  State<MedicalCard> createState() => _MedicalCardState();
}

class _MedicalCardState extends State<MedicalCard> {
  bool _isEditing = false;
  late List<String> _selectedConditions;
  late TextEditingController _allergiesController;

  final List<String> _availableConditions = ["Diabetes", "Hypertension", "Asthma", "Thyroid", "Cholesterol", "None"];

  @override
  void initState() {
    super.initState();
    _initData();
  }

  void _initData() {
    _selectedConditions = List.from(widget.user.medicalConditions);
    if (_selectedConditions.isEmpty) {
      _selectedConditions.add("None");
    }
    _allergiesController = TextEditingController(text: widget.user.allergies);
  }

  @override
  void didUpdateWidget(covariant MedicalCard oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.user != widget.user) {
      _initData();
    }
  }

  @override
  void dispose() {
    _allergiesController.dispose();
    super.dispose();
  }

  void _onChipSelected(bool selected, String condition) {
    setState(() {
      if (condition == "None") {
        if (selected) {
          _selectedConditions.clear();
          _selectedConditions.add("None");
        }
      } else {
        _selectedConditions.remove("None");
        if (selected) {
          _selectedConditions.add(condition);
        } else {
          _selectedConditions.remove(condition);
        }
        if (_selectedConditions.isEmpty) {
          _selectedConditions.add("None");
        }
      }
    });
  }

  void _saveChanges() {
    // If none is selected, ensure it is represented
    if (_selectedConditions.isEmpty) {
      _selectedConditions.add("None");
    }
    widget.onSave(_selectedConditions, _allergiesController.text.trim());
    setState(() {
      _isEditing = false;
    });
  }

  void _cancel() {
    setState(() {
      _isEditing = false;
      _initData();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Container(
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
        border: Border.all(color: Colors.grey.shade100),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Card Header
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 16, 16, 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: AppTheme.primaryColor.withOpacity(0.08),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: const Icon(
                        Icons.medical_services_outlined,
                        color: AppTheme.primaryColor,
                        size: 20,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Text(
                      "Medical Information",
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: AppTheme.textColorPrimary,
                          ),
                    ),
                  ],
                ),
                if (!_isEditing)
                  IconButton(
                    icon: const Icon(Icons.edit_outlined, color: AppTheme.primaryColor),
                    onPressed: () => setState(() => _isEditing = true),
                  ),
              ],
            ),
          ),
          const Divider(height: 1, color: Color(0xFFF1F1F1)),
          
          AnimatedSwitcher(
            duration: const Duration(milliseconds: 250),
            child: _isEditing ? _buildEditForm() : _buildDisplayView(),
          ),
        ],
      ),
    );
  }

  Widget _buildDisplayView() {
    return Padding(
      padding: const EdgeInsets.all(20),
      key: const ValueKey('medical_display'),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "Medical Conditions",
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: AppTheme.primaryColor,
            ),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: widget.user.medicalConditions.map((cond) {
              final isNone = cond.toLowerCase() == 'none';
              return Chip(
                label: Text(
                  cond,
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: isNone ? Colors.grey.shade700 : Colors.white,
                  ),
                ),
                backgroundColor: isNone ? Colors.grey.shade200 : AppTheme.primaryColor,
                side: BorderSide.none,
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(20),
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: 16),
          const Text(
            "Known Allergies",
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: AppTheme.primaryColor,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            widget.user.allergies.isNotEmpty ? widget.user.allergies : "No known allergies listed.",
            style: TextStyle(
              fontSize: 13,
              height: 1.4,
              color: widget.user.allergies.isNotEmpty ? AppTheme.textColorPrimary : Colors.grey.shade500,
              fontStyle: widget.user.allergies.isNotEmpty ? FontStyle.normal : FontStyle.italic,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEditForm() {
    return Padding(
      padding: const EdgeInsets.all(20),
      key: const ValueKey('medical_edit'),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "Select Medical Conditions",
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: AppTheme.textColorPrimary,
            ),
          ),
          const SizedBox(height: 10),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _availableConditions.map((cond) {
              final isSelected = _selectedConditions.contains(cond);
              return FilterChip(
                selected: isSelected,
                label: Text(
                  cond,
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: isSelected ? Colors.white : AppTheme.textColorPrimary,
                  ),
                ),
                backgroundColor: AppTheme.cardColor,
                selectedColor: AppTheme.primaryColor,
                checkmarkColor: Colors.white,
                side: BorderSide(color: isSelected ? AppTheme.primaryColor : Colors.grey.shade200),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(20),
                ),
                onSelected: (selected) => _onChipSelected(selected, cond),
              );
            }).toList(),
          ),
          const SizedBox(height: 16),
          const Text(
            "Known Allergies",
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: AppTheme.textColorPrimary,
            ),
          ),
          const SizedBox(height: 6),
          TextField(
            controller: _allergiesController,
            maxLines: 3,
            style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
            decoration: const InputDecoration(
              hintText: "Enter known allergies (e.g. Penicillin, Dust Allergy, etc.)",
            ),
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: _cancel,
                  style: OutlinedButton.styleFrom(
                    foregroundColor: Colors.grey.shade700,
                    side: BorderSide(color: Colors.grey.shade300),
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                    ),
                  ),
                  child: const Text("Cancel"),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: ElevatedButton(
                  onPressed: _saveChanges,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.primaryColor,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    minimumSize: Size.zero,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                    ),
                  ),
                  child: const Text("Update Medical Info"),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
