class RefillModel {
  final String medicineName;
  final int daysRemaining;
  final double percentageRemaining;

  RefillModel({
    required this.medicineName,
    required this.daysRemaining,
    required this.percentageRemaining,
  });

  static RefillModel get mock => RefillModel(
        medicineName: "Crocin 650",
        daysRemaining: 3,
        percentageRemaining: 0.70, // Represents 70% Remaining
      );
}
