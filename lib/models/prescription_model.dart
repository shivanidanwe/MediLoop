class PrescriptionModel {
  final String id;
  final String uploadDate;
  final String status; // "Verified", "Pending", "Rejected"
  final String fileName;
  final String? filePath;

  PrescriptionModel({
    required this.id,
    required this.uploadDate,
    required this.status,
    required this.fileName,
    this.filePath,
  });

  static List<PrescriptionModel> get mockPrescriptions => [
        PrescriptionModel(
          id: "p1",
          uploadDate: "2026-06-28",
          status: "Verified",
          fileName: "Crocin_Prescription.pdf",
        ),
        PrescriptionModel(
          id: "p2",
          uploadDate: "2026-07-02",
          status: "Pending",
          fileName: "Asthma_Inhaler_Rx.jpg",
        ),
      ];
}
