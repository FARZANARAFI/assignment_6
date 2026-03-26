import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:securebank/home/user_model.dart';

class UserDatabaseService {
  final String uid;

  UserDatabaseService({required this.uid});

  // Stream to listen to changes in user document
  Stream<UserModel> get userData {
    return FirebaseFirestore.instance
        .collection('securebankUsers')
        .doc(uid)
        .snapshots()
        .map((snapshot) => _userDataFromSnapshot(snapshot));
  }

  // Method to convert Firestore snapshot to UserModel object
  UserModel _userDataFromSnapshot(DocumentSnapshot snapshot) {
    Map<String, dynamic> data = snapshot.data() as Map<String, dynamic>;
    return UserModel(
      userId: uid,
      userName: data['userName'] ?? '',
      userEmail: data['userEmail'] ?? '',
      userBalance: (data['userBalance'] ?? 0).toDouble(),
      userAddress: data['userAddress'] ?? '',
      userAge: data['userAge'] ?? '',
      userAlias: data['userAlias'] ?? '',
      userGender: data['userGender'] ?? '',
      userPhone: data['userPhone'] ?? '',
      userProfileImage: data['userProfileImage'] ?? '',
      userRole: data['userRole'] ?? '',
      userRoleVerified: data['userRoleVerified'] ?? false,
      accountNumber:  data['accountNumber'] ?? '',
    );
  }
}
