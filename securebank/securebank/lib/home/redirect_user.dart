import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:securebank/home/admin_page.dart';
import 'package:securebank/home/bank_manager.dart';
import 'package:securebank/home/customer_page.dart';
import 'package:securebank/home/customer_support_page.dart';
import 'package:securebank/home/verify.dart';

class RedirectUser extends StatefulWidget {
  const RedirectUser({super.key});

  @override
  State<RedirectUser> createState() => _RedirectUserState();
}

class _RedirectUserState extends State<RedirectUser> {
  bool isVerified = false;
  FirebaseAuth auth = FirebaseAuth.instance;
  List<Widget> screens = [
     CustomerPage(userId: FirebaseAuth.instance.currentUser!.uid,),
    const BankManagerPage(),
    const CustomerSupportPage(),
    const AdminPage(),
  ];
  @override
  void initState() {
    super.initState();
    getUserRole(auth.currentUser!.uid);
    getUserRoleVerification(auth.currentUser!.uid);
  }

  Future<bool> getUserRoleVerification(String uid) async {
    DocumentSnapshot userDoc = await FirebaseFirestore.instance
        .collection('securebankUsers')
        .doc(uid)
        .get();

    if (userDoc.exists) {
      isVerified = userDoc['userRoleVerified'];
      return userDoc['userRoleVerified'];
    } else {
      return false;
    }
  }

  int index = 0;
  Future<int?> getUserRole(String uid) async {
    DocumentSnapshot userDoc = await FirebaseFirestore.instance
        .collection('securebankUsers')
        .doc(uid)
        .get();

    if (userDoc.exists) {
      setState(() {
        if (userDoc['userRole'] == 'Customer') {
          index = 0;
        } else if (userDoc['userRole'] == 'Bank Manager') {
          index = 1;
        } else if (userDoc['userRole'] == 'Customer Support') {
          index = 2;
        } else if (userDoc['userRole'] == 'Admin') {
          index = 3;
        }
      });

      return index;
    } else {
      return null;
    }
  }

  @override
  Widget build(BuildContext context) {
    return isVerified ? screens[index] : const VerificationScreen();
  }
}
