
import 'package:flutter/material.dart';
import 'package:lottie/lottie.dart';

class VerificationScreen extends StatefulWidget {
  const VerificationScreen({super.key});

  @override
  State<VerificationScreen> createState() => _VerificationScreenState();
}

class _VerificationScreenState extends State<VerificationScreen> {

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Lottie.asset('assets/images/verification.json'),
            const SizedBox(
              height: 20,
            ),
            const Text(
              'Your account is in verification..',
              style: TextStyle(fontSize: 23),
            ),
          ],
        ),
      ),
    );
  }
}
