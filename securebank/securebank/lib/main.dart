import 'dart:math';

import 'package:flutter/cupertino.dart';
import 'package:securebank/constants.dart';
import 'package:securebank/home/redirect_user.dart';

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart' hide EmailAuthProvider;
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_ui_auth/firebase_ui_auth.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:securebank/pin_verify.dart';
import 'firebase_options.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
  FirebaseUIAuth.configureProviders([EmailAuthProvider()]);
  runApp(const MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData.light().copyWith(
        primaryColor: defaultPropertyBackgroundColour,
        useMaterial3: true,
        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
      ),
      home: const AuthWidget(),
    );
  }
}

class AuthWidget extends StatefulWidget {
  const AuthWidget({super.key});

  @override
  State<AuthWidget> createState() => _AuthWidgetState();
}

class _AuthWidgetState extends State<AuthWidget> {
  int segmentedControlGroupValue = 0;
  final Map<int, Widget> myTabs = const <int, Widget>{
    0: Text('Customer'),
    1: Text('Manager'),
    2: Text('Support'),
    3: Text('Admin'),
  };
  @override
  Widget build(BuildContext context) {
   
    return StreamBuilder<User?>(
      stream: FirebaseAuth.instance.authStateChanges(),
      builder: (context, snapshot) {
        if (snapshot.hasData) {
          return PinPasswordScreen();
        }
        return SignInScreen(
          subtitleBuilder: (context, action) {
            final actionText = switch (action) {
              AuthAction.signIn => 'Please sign in to continue.',
              AuthAction.signUp => 'Please create an account to continue',
              _ => throw Exception('Invalid action: $action'),
            };

            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Text('Welcome to BlockBank Guardian! $actionText.'),
            );
          },
          footerBuilder: (context, action) {
            final actionText = switch (action) {
              AuthAction.signIn => 'signing in',
              AuthAction.signUp => 'registering',
              _ => throw Exception('Invalid action: $action'),
            };

            return Column(
              children: [
                const SizedBox(
                  height: 20,
                ),
                CupertinoSlidingSegmentedControl(
                    groupValue: segmentedControlGroupValue,
                    children: myTabs,
                    onValueChanged: (i) {
                      setState(() {
                        segmentedControlGroupValue = i!;
                      });

                      print(segmentedControlGroupValue);
                    }),
                Center(
                  child: Padding(
                    padding: const EdgeInsets.only(top: 16),
                    child: Text(
                      'By $actionText, you agree to our terms and conditions.',
                      style: const TextStyle(color: Colors.grey),
                    ),
                  ),
                ),
              ],
            );
          },
          headerBuilder: (context, constraints, shrinkOffset) {
            return Center(
              child: Image.asset('assets/images/icon.png',
                  width: 100, height: 100),
            );
          },
          providers: [EmailAuthProvider()],
          actions: [
            AuthStateChangeAction<UserCreated>((context, state) async {
              _createUserDocument(state.credential.user!);
              if (kDebugMode) {
                print('New User Created');
              }
            }),
            AuthStateChangeAction<SignedIn>((context, state) {}),
          ],
        );
      },
    );
  }

  void _createUserDocument(User user) {
    FirebaseFirestore.instance.collection('securebankUsers').doc(user.uid).set({
      'userId': user.uid,
      'userAlias': "User",
      'userName': "User",
      'userEmail': user.email,
      'userRole': segmentedControlGroupValue == 0
          ? 'Customer'
          : segmentedControlGroupValue == 1
              ? 'Bank Manager'
              : segmentedControlGroupValue == 2
                  ? 'Customer Support'
                  : segmentedControlGroupValue == 3
                      ? 'Admin'
                      : 'Customer',
      'userRoleVerified': false,
      'userPhone': '',
      'userGender': '',
      'userAge': '',
      'userBalance': 0,
      'userProfileImage':
          'https://cdn-icons-png.flaticon.com/512/666/666201.png',
      'userAddress': '',
      'accountNumber': generateRandomAccountNumber(),
    });


    
  }

  String generateRandomAccountNumber() {
    // You can customize the length of the account number as needed
    final int length = 6;
    final String prefix = 'SB';

    // Generate a random alphanumeric string
    final String characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    final Random random = Random();
    String accountNumber = prefix;

    for (int i = 0; i < length; i++) {
      accountNumber += characters[random.nextInt(characters.length)];
    }

    return accountNumber;
  }
}
