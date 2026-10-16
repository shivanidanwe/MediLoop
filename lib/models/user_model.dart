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

  factory UserModel.fromJson(Map<String, dynamic> json) {
    // Parse nested addresses if available
    String addressStr = json['address'] ?? '';
    if (addressStr.isEmpty && json['addresses'] != null && (json['addresses'] as List).isNotEmpty) {
      final addr = (json['addresses'] as List).first;
      if (addr is Map<String, dynamic>) {
        final house = addr['house_number'] != null && addr['house_number'].toString().isNotEmpty ? "${addr['house_number']}, " : "";
        addressStr = "$house${addr['street'] ?? ''}, ${addr['city'] ?? ''}, ${addr['state'] ?? ''} - ${addr['pincode'] ?? ''}".trim();
      }
    }

    // Parse medical info
    List<String> conditions = [];
    String allergiesStr = '';
    if (json['medical_info'] != null && json['medical_info'] is Map<String, dynamic>) {
      final medInfo = json['medical_info'] as Map<String, dynamic>;
      final rawCond = medInfo['medical_conditions'] ?? medInfo['conditions'];
      if (rawCond is List) {
        conditions = List<String>.from(rawCond);
      } else if (rawCond is String && rawCond.isNotEmpty && rawCond != 'None') {
        conditions = rawCond.split(',').map((e) => e.trim()).where((e) => e.isNotEmpty).toList();
      }
      final rawAllergies = medInfo['allergies'];
      if (rawAllergies is List) {
        allergiesStr = rawAllergies.join('\n');
      } else if (rawAllergies is String) {
        allergiesStr = rawAllergies;
      }
    } else if (json['medicalConditions'] is List) {
      conditions = List<String>.from(json['medicalConditions']);
      allergiesStr = json['allergies'] ?? '';
    }

    // Parse emergency contact
    String rel = '';
    String emerPhone = '';
    if (json['emergency_contact'] != null && json['emergency_contact'] is Map<String, dynamic>) {
      final emer = json['emergency_contact'] as Map<String, dynamic>;
      rel = emer['relationship'] ?? '';
      emerPhone = emer['contact_number'] ?? emer['phone_number'] ?? '';
    } else {
      rel = json['emergencyRelationship'] ?? '';
      emerPhone = json['emergencyPhone'] ?? json['contact_number'] ?? '';
    }

    // Calculate age if date_of_birth present
    int userAge = json['age'] ?? 0;
    if (userAge == 0 && json['date_of_birth'] != null) {
      try {
        final dob = DateTime.parse(json['date_of_birth']);
        userAge = DateTime.now().year - dob.year;
      } catch (_) {}
    }

    return UserModel(
      name: (json['full_name'] ?? json['name'] ?? '').toString().trim(),
      phoneNumber: json['mobile_number'] ?? json['phoneNumber'] ?? '',
      email: json['email'] ?? '',
      age: userAge,
      gender: json['gender'] ?? '',
      address: addressStr,
      profilePic: json['profile_image'] ?? json['profilePic'],
      medicalConditions: conditions,
      allergies: allergiesStr,
      emergencyRelationship: rel,
      emergencyPhone: emerPhone,
      pushNotifications: json['pushNotifications'] ?? true,
      emailNotifications: json['emailNotifications'] ?? false,
      smsNotifications: json['smsNotifications'] ?? true,
      darkMode: json['darkMode'] ?? false,
      language: json['language'] ?? 'English',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'full_name': name,
      'mobile_number': phoneNumber,
      'email': email,
      'age': age,
      'gender': gender,
      'address': address,
      'profile_image': profilePic,
      'medicalConditions': medicalConditions,
      'allergies': allergies,
      'emergencyRelationship': emergencyRelationship,
      'emergencyPhone': emergencyPhone,
      'pushNotifications': pushNotifications,
      'emailNotifications': emailNotifications,
      'smsNotifications': smsNotifications,
      'darkMode': darkMode,
      'language': language,
    };
  }

  static UserModel get empty => UserModel(
        name: "",
        phoneNumber: "",
        email: "",
        age: 0,
        gender: "",
        address: "",
        profilePic: null,
        medicalConditions: [],
        allergies: "",
        emergencyRelationship: "",
        emergencyPhone: "",
        pushNotifications: false,
        emailNotifications: false,
        smsNotifications: false,
        darkMode: false,
        language: "English",
      );
}
