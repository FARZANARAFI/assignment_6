import 'package:securebank/services/firestore_service.dart';
import 'package:firebase_ui_auth/firebase_ui_auth.dart';
import 'package:flutter/material.dart';

class ProfilePage extends StatefulWidget {
  const ProfilePage({super.key});

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  @override
  Widget build(BuildContext context) {
    return ProfileScreen(
      providers: [EmailAuthProvider()],
      actions: [
        AccountDeletedAction((context, user) {
          final FirestoreService firestoreService = FirestoreService();
          firestoreService.deleteDocument('securebankUsers', user.uid);
        })
      ],
    );
  }
}
