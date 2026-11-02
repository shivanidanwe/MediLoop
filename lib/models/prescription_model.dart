class PrescriptionModel {
  final String id;
  final String uploadDate;
  final String status; // "Verified", "Pending Verification", "Approved", "Rejected"
  final String fileName;
  final String? filePath;
  final String? extractedText;
  final List<dynamic> items;

  PrescriptionModel({
    required this.id,
    required this.uploadDate,
    required this.status,
    required this.fileName,
    this.filePath,
    this.extractedText,
    this.items = const [],
  });

  factory PrescriptionModel.fromJson(Map<String, dynamic> json) {
    final uploadDateStr = json['uploaded_at']?.toString().split('T').first ?? '';
    final statusRaw = (json['verification_status'] ?? 'PENDING_VERIFICATION').toString();
    String formattedStatus = statusRaw.replaceAll('_', ' ');
    if (formattedStatus.toUpperCase() == 'APPROVED') {
      formattedStatus = 'Verified';
    }

    return PrescriptionModel(
      id: (json['id'] ?? '').toString(),
      uploadDate: uploadDateStr,
      status: formattedStatus,
      fileName: json['original_filename'] ?? 'Prescription.jpg',
      filePath: json['uploaded_image_path'],
      extractedText: json['extracted_text'],
      items: json['items'] is List ? json['items'] : const [],
    );
  }

  static List<PrescriptionModel> get mockPrescriptions => [
        PrescriptionModel(
          id: "p1",
          uploadDate: "2026-06-28",
          status: "Verified",
          fileName: "Crocin_Prescription.pdf",
          extractedText: "Tab Crocin 650mg - 1-0-1 (After Food)\nTab Cetirizine 10mg - 0-0-1 (Bedtime)\nDuration: 3 days",
        ),
        PrescriptionModel(
          id: "p2",
          uploadDate: "2026-07-02",
          status: "Pending Verification",
          fileName: "Asthma_Inhaler_Rx.jpg",
          extractedText: "Budecort 200 Inhaler - 2 puffs twice daily\nLevolin Inhaler - SOS for acute breathlessness",
        ),
      ];
}
