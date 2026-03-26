import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:lottie/lottie.dart';
import 'package:securebank/home/user_model.dart';
import 'package:securebank/home/user_provider.dart';
import 'package:securebank/services/etherium_contract_service.dart';

class TransferMoneyPage extends StatefulWidget {
  final String userId;

  TransferMoneyPage({required this.userId});

  @override
  _TransferMoneyPageState createState() => _TransferMoneyPageState();
}

class _TransferMoneyPageState extends State<TransferMoneyPage> {
  final TextEditingController amountController = TextEditingController();
  final TextEditingController recipientController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Transfer Money'),
      ),
      body: SingleChildScrollView(
        child: StreamBuilder(
          stream: UserDatabaseService(uid: widget.userId).userData,
          builder: (context, AsyncSnapshot<UserModel> snapshot) {
            if (!snapshot.hasData) {
              return Center(
                child: CircularProgressIndicator(),
              );
            }

            UserModel currentUser = snapshot.data!;

            return Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Lottie.asset('assets/images/transfer.json'),
                  Card(
                    elevation: 5.0,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(15.0),
                    ),
                    child: ListTile(
                      title: Text(
                        'Your Balance:',
                        style: TextStyle(fontSize: 18.0),
                      ),
                      subtitle: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            '₹${currentUser.userBalance.toStringAsFixed(2)}',
                            style: TextStyle(
                              fontSize: 24.0,
                              fontWeight: FontWeight.bold,
                              color: Colors.green,
                            ),
                          ),
                          Icon(
                            Icons.account_balance_wallet,
                            color: Colors.blue,
                          ),
                        ],
                      ),
                    ),
                  ),
                  SizedBox(height: 20),
                  TextField(
                    controller: recipientController,
                    decoration: InputDecoration(
                      labelText: 'Recipient Account Number',
                      prefixIcon: Icon(Icons.person),
                    ),
                  ),
                  SizedBox(height: 10),
                  TextField(
                    controller: amountController,
                    keyboardType:
                        TextInputType.numberWithOptions(decimal: true),
                    decoration: InputDecoration(
                      labelText: 'Amount to Transfer',
                      prefixIcon: Icon(Icons.monetization_on),
                    ),
                  ),
                  SizedBox(height: 20),
                  ElevatedButton(
                    onPressed: () {
                      double amount =
                          double.tryParse(amountController.text) ?? 0.0;
                      String recipientUserId = recipientController.text.trim();

                      // Implement logic to transfer money (update Firestore documents)
                      if (amount > 0 && recipientUserId.isNotEmpty) {
                        transferMoney(currentUser, recipientUserId, amount);
                      } else {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text('Please enter valid details.'),
                          ),
                        );
                      }
                    },
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.send),
                        SizedBox(width: 8.0),
                        Text('Transfer Money'),
                      ],
                    ),
                  ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }

  void transferMoney(
      UserModel sender, String recipientAccountNumber, double amount) {
    if (sender.userBalance < amount) {
      // Show an error dialog if the sender does not have enough balance
      showDialog(
        context: context,
        builder: (BuildContext context) {
          return AlertDialog(
            title: Text('Error'),
            content: Text('Insufficient balance!'),
            actions: <Widget>[
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
      return; // Exit the method if the sender does not have enough balance
    }

    // Show circular progress indicator while transferring money
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
          content: CircularProgressIndicator(),
        );
      },
    );

    final ethereumService = EthereumContractService();

 

    ethereumService
        .addTransactionToBlockchain(
      'debit',
amount.toInt(),
      recipientAccountNumber,
      FirebaseAuth.instance.currentUser!.uid,
    )
        .then((response) {
      print('Transaction hash: ${response['transaction_hash']}');
    }).catchError((error) {
      print('Error: $error');
    });

    // Query Firestore to find recipient based on account number
    FirebaseFirestore.instance
        .collection('securebankUsers')
        .where('accountNumber', isEqualTo: recipientAccountNumber)
        .get()
        .then((querySnapshot) {
      if (querySnapshot.docs.isNotEmpty) {
        // Recipient found
        FirebaseFirestore.instance.runTransaction((transaction) async {
          // Deduct amount from sender's balance
          transaction.update(
            FirebaseFirestore.instance
                .collection('securebankUsers')
                .doc(sender.userId),
            {'userBalance': sender.userBalance - amount},
          );

          // Add amount to recipient's balance
          transaction.update(
            FirebaseFirestore.instance
                .collection('securebankUsers')
                .doc(querySnapshot.docs.first.id),
            {
              'userBalance':
                  querySnapshot.docs.first.data()['userBalance'] + amount
            },
          );

          // Store transaction information in userTransactions subcollection
          transaction.set(
            FirebaseFirestore.instance
                .collection('securebankUsers')
                .doc(sender.userId)
                .collection('userTransactions')
                .doc(), // Using auto-generated document ID
            {
              'type': 'debit',
              'amount': amount,
              'recipientAccountNumber': recipientAccountNumber,
              'timestamp': DateTime.now(),
            },
          );

          // Store credit transaction information for the recipient
          transaction.set(
            FirebaseFirestore.instance
                .collection('securebankUsers')
                .doc(querySnapshot.docs.first.id)
                .collection('userTransactions')
                .doc(), // Using auto-generated document ID
            {
              'type': 'credit',
              'amount': amount,
              'senderAccountNumber': sender.accountNumber,
              'timestamp': DateTime.now(),
            },
          );
        }).then((_) {
          // Hide the progress dialog
          Navigator.of(context).pop();

          // Show a success dialog upon successful transfer
          showDialog(
            context: context,
            builder: (BuildContext context) {
              return AlertDialog(
                title: Text('Success'),
                content: SizedBox(
                  width: 200,
                  height: 200,
                  child: Column(
                    children: [
                      SizedBox(
                        child: Lottie.asset('assets/images/success.json'),
                        width: 150,
                        height: 150,
                      ),
                      Text('Money transferred successfully!'),
                    ],
                  ),
                ),
                actions: <Widget>[
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
        });
      } else {
        // Hide the progress dialog
        Navigator.of(context).pop();

        // Show an error dialog if the recipient account number is not found
        showDialog(
          context: context,
          builder: (BuildContext context) {
            return AlertDialog(
              title: Text('Error'),
              content: Text('Recipient account number not found!'),
              actions: <Widget>[
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
    }).catchError((error) {
      // Hide the progress dialog
      Navigator.of(context).pop();

      // Show an error dialog if an error occurs during the query
      showDialog(
        context: context,
        builder: (BuildContext context) {
          return AlertDialog(
            title: Text('Error'),
            content: Text('Error: $error'),
            actions: <Widget>[
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
    });
  }
}
