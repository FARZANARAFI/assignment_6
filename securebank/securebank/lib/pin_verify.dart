import 'package:flutter/material.dart';
import 'package:securebank/home/redirect_user.dart';

class PinPasswordScreen extends StatefulWidget {
  @override
  _PinPasswordScreenState createState() => _PinPasswordScreenState();
}

class _PinPasswordScreenState extends State<PinPasswordScreen> {
  String pin = '';
  bool isVerified = false;

  // Predefined PIN
  final String correctPin = '1234';

  @override
  Widget build(BuildContext context) {
    return 
    isVerified ? RedirectUser() :
    Scaffold(
      appBar: AppBar( centerTitle: true,
        title: Text('PIN Verification'),

      ),
      backgroundColor: Colors.white,
      body: Padding(
        padding: EdgeInsets.all(20.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Image.asset(
              'assets/images/icon.png', // Your PIN icon image asset
              height: 120,
            ),
            SizedBox(height: 20),
            TextField(
              onChanged: (value) {
                setState(() {
                  pin = value;
                });
              },
              keyboardType: TextInputType.number,
              obscureText: true,
              cursorColor: Colors.blue,
              style: TextStyle(
                fontSize: 20,
                color: Colors.black,
              ),
              decoration: InputDecoration(
                labelText: 'Enter PIN',
                
               
              ),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                if (pin == correctPin) {
                  // Correct PIN, set isVerified to true
                  setState(() {
                    isVerified = true;
                  });
                  // Navigate to next screen or perform any action
                } else {
                  // Incorrect PIN, show error message
                  showDialog(
                    context: context,
                    builder: (context) {
                      return AlertDialog(
                        title: Text('Error'),
                        content: Text('Incorrect PIN. Please try again.'),
                        actions: [
                          TextButton(
                            onPressed: () {
                              Navigator.of(context).pop();
                            },
                            child: Text('OK'),
                          ),
                        ],
                      );
                    },
                  );
                }
              },
              style: ElevatedButton.styleFrom(
        
                padding: EdgeInsets.symmetric(horizontal: 40, vertical: 15),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(30),
                ),
              ),
              child: Text(
                'Verify PIN',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            if (isVerified)
              Padding(
                padding: EdgeInsets.only(top: 20),
                child: Text(
                  'PIN Verified!',
                  style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold, fontSize: 20),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
