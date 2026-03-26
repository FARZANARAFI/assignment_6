class UserModel {
  final String userId;
  final String userName;
  final String userEmail;
  final double userBalance;
  final String userAddress;
  final String userAge;
  final String userAlias;
  final String userGender;
  final String userPhone;
  final String userProfileImage;
  final String userRole;
  final String accountNumber;
  final bool userRoleVerified;

  UserModel({
    required this.userId,
    required this.userName,
    required this.userEmail,
    required this.userBalance,
    required this.userAddress,
    required this.userAge,
    required this.userAlias,
    required this.userGender,
    required this.userPhone,
    required this.userProfileImage,
    required this.userRole,
    required this.accountNumber,
    required this.userRoleVerified,
  });

  factory UserModel.fromMap(Map<String, dynamic> map) {
    return UserModel(
      userId: map['userId'],
      userName: map['userName'],
      userEmail: map['userEmail'],
 userBalance: (map['userBalance'] ?? 0).toDouble(), 
      userAddress: map['userAddress'] ?? '',
      userAge: map['userAge'] ?? '',
      userAlias: map['userAlias'] ?? '',
      userGender: map['userGender'] ?? '',
      userPhone: map['userPhone'] ?? '',
      userProfileImage: map['userProfileImage'] ?? '',
      userRole: map['userRole'] ?? '',
      accountNumber: map['accountNumber'] ?? '',
      userRoleVerified: map['userRoleVerified'] ?? false,
    );
  }
}
