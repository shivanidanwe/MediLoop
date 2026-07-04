class UserModel {
  final String name;
  final String phoneNumber;
  final String email;
  final int age;
  final String gender;
  final String address; // default address representation for backwards compatibility
  final String? profilePic;
  
  // Medical Info
  final List<String> medicalConditions;
  final String allergies;
  
  // Emergency Contact
  final String emergencyRelationship;
  final String emergencyPhone;
  
  // Settings/Preferences
  final bool pushNotifications;
  final bool emailNotifications;
  final bool smsNotifications;
  final bool darkMode;
  final String language;

  UserModel({
    required this.name,
    required this.phoneNumber,
    required this.email,
    required this.age,
    required this.gender,
    required this.address,
    this.profilePic,
    required this.medicalConditions,
    required this.allergies,
    required this.emergencyRelationship,
    required this.emergencyPhone,
    required this.pushNotifications,
    required this.emailNotifications,
    required this.smsNotifications,
    required this.darkMode,
    required this.language,
  });

  UserModel copyWith({
    String? name,
    String? phoneNumber,
    String? email,
    int? age,
    String? gender,
    String? address,
    String? profilePic,
    List<String>? medicalConditions,
    String? allergies,
    String? emergencyRelationship,
    String? emergencyPhone,
    bool? pushNotifications,
    bool? emailNotifications,
    bool? smsNotifications,
    bool? darkMode,
    String? language,
  }) {
    return UserModel(
      name: name ?? this.name,
      phoneNumber: phoneNumber ?? this.phoneNumber,
      email: email ?? this.email,
      age: age ?? this.age,
      gender: gender ?? this.gender,
      address: address ?? this.address,
      profilePic: profilePic ?? this.profilePic,
      medicalConditions: medicalConditions ?? this.medicalConditions,
      allergies: allergies ?? this.allergies,
      emergencyRelationship: emergencyRelationship ?? this.emergencyRelationship,
      emergencyPhone: emergencyPhone ?? this.emergencyPhone,
      pushNotifications: pushNotifications ?? this.pushNotifications,
      emailNotifications: emailNotifications ?? this.emailNotifications,
      smsNotifications: smsNotifications ?? this.smsNotifications,
      darkMode: darkMode ?? this.darkMode,
      language: language ?? this.language,
    );
  }

  static UserModel get mock => UserModel(
        name: "Shivani Danwe",
        phoneNumber: "+91 9876543210",
        email: "shivani@gmail.com",
        age: 26,
        gender: "Female",
        address: "Flat 203, Rosewood Apartments, Pune, Maharashtra",
        profilePic: null,
        medicalConditions: ["Diabetes", "Hypertension"],
        allergies: "Penicillin\nDust Allergy",
        emergencyRelationship: "Brother",
        emergencyPhone: "+91 9988776655",
        pushNotifications: true,
        emailNotifications: false,
        smsNotifications: true,
        darkMode: false,
        language: "English",
      );
}
