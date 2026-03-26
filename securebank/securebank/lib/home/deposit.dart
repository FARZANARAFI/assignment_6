import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

class DepositMoneyPage extends StatefulWidget {
  @override
  _DepositMoneyPageState createState() => _DepositMoneyPageState();
}

class _DepositMoneyPageState extends State<DepositMoneyPage> {
  final TextEditingController accountNumberController = TextEditingController();
  final TextEditingController amountController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Deposit Money'),
      ),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Enter the account number and amount to deposit:',
              style: TextStyle(
                fontSize: 18.0,
                fontWeight: FontWeight.bold,
                color: Colors.blue,
              ),
            ),
            SizedBox(height: 20.0),
            TextField(
              controller: accountNumberController,
              keyboardType: TextInputType.text,
              decoration: InputDecoration(
                labelText: 'Account Number',
                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 16.0),
            TextField(
              controller: amountController,
              keyboardType: TextInputType.numberWithOptions(decimal: true),
              decoration: InputDecoration(
                labelText: 'Amount',
                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 20.0),
            Center(
              child: ElevatedButton(
                onPressed: () {
                  _depositMoney();
                },
                child: Text('Deposit'),
                style: ElevatedButton.styleFrom(
                  padding: EdgeInsets.symmetric(horizontal: 40.0, vertical: 16.0),
                  textStyle: TextStyle(fontSize: 18.0),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _depositMoney() {
    String accountNumber = accountNumberController.text.trim();
    double amount = double.tryParse(amountController.text.trim()) ?? 0.0;

    if (accountNumber.isEmpty || amount <= 0) {
      _showSnackbar('Please enter a valid account number and amount.');
      return;
    }

    FirebaseFirestore.instance
        .collection('securebankUsers')
        .where('accountNumber', isEqualTo: accountNumber)
        .get()
        .then((querySnapshot) {
      if (querySnapshot.docs.isNotEmpty) {
        // Update the user's balance
        String userId = querySnapshot.docs.first.id;
        double currentBalance = querySnapshot.docs.first.data()['userBalance'] ?? 0.0;
        double updatedBalance = currentBalance + amount;

        FirebaseFirestore.instance
            .collection('securebankUsers')
            .doc(userId)
            .update({'userBalance': updatedBalance})
            .then((_) {
          _showSnackbar('Deposit successful.');
        }).catchError((error) {
          _showSnackbar('Failed to deposit. Error: $error');
        });
      } else {
        _showSnackbar('Account number not found.');
      }
    }).catchError((error) {
      _showSnackbar('Failed to deposit. Error: $error');
    });
  }

  void _showSnackbar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
  }
}
