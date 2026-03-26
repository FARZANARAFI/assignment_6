import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:lottie/lottie.dart';
import 'package:securebank/home/transfer_money.dart';
import 'package:securebank/home/user_model.dart';
import 'package:securebank/home/user_provider.dart';

class CustomerPage extends StatelessWidget {
  final String userId;

  CustomerPage({required this.userId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('BlockBank Guardian'),
        actions: [
          IconButton(
            icon: Icon(Icons.exit_to_app),
            onPressed: () {
              FirebaseAuth.instance.signOut();
            },
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            flex: 4,
            child: SingleChildScrollView(
              child: StreamBuilder(
                stream: UserDatabaseService(uid: userId).userData,
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
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Lottie.asset('assets/images/bank_home.json'),
                        SizedBox(
                          width: 320,
                          child: Card(
                            color: Colors.blue[70],
                            elevation: 5.0,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(15.0),
                            ),
                            child: Padding(
                              padding: const EdgeInsets.all(16.0),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    mainAxisAlignment:
                                        MainAxisAlignment.spaceBetween,
                                    children: [
                                      Text(
                                        'Account Balance',
                                        style: TextStyle(
                                          fontSize: 18.0,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      Icon(
                                        Icons.account_balance_wallet,
                                        color: Colors.blue,
                                      ),
                                    ],
                                  ),
                                  SizedBox(height: 10.0),
                                  Text(
                                    '₹${currentUser.userBalance.toStringAsFixed(2)}',
                                    style: TextStyle(
                                      fontSize: 24.0,
                                      fontWeight: FontWeight.bold,
                                      color: Colors.green,
                                    ),
                                  ),
                                  SizedBox(height: 10.0),
                                  Text(
                                    'Account Number: ${currentUser.accountNumber}',
                                    style: TextStyle(
                                      fontSize: 16.0,
                                      color: Colors.grey,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                        SizedBox(height: 20),
                        ElevatedButton(
                          onPressed: () {
                            // Navigate to the transfer money page
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (context) =>
                                    TransferMoneyPage(userId: userId),
                              ),
                            );
                          },
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.monetization_on),
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
          ),
          SizedBox(height: 20),
          Text(
            'Transaction History',
            style: TextStyle(
              fontSize: 20.0,
              fontWeight: FontWeight.bold,
            ),
            textAlign: TextAlign.center,
          ),
          SizedBox(height: 10),
          Expanded(
            flex: 2,
            child: StreamBuilder(
              stream: FirebaseFirestore.instance
                  .collection('securebankUsers')
                  .doc(userId)
                  .collection('userTransactions')
                  .orderBy('timestamp', descending: true)
                  .snapshots(),
              builder: (context, AsyncSnapshot<QuerySnapshot> snapshot) {
                if (!snapshot.hasData) {
                  return Center(
                    child: CircularProgressIndicator(),
                  );
                }

                return ListView.builder(
                  shrinkWrap: true,
                  itemCount: snapshot.data!.docs.length,
                  itemBuilder: (context, index) {
                    var transaction = snapshot.data!.docs[index];
                    return ListTile(
                      leading: transaction['type'] == 'debit'
                          ? Icon(Icons.arrow_upward, color: Colors.red)
                          : Icon(Icons.arrow_downward, color: Colors.green),
                      title: Text(
                          transaction['type'] == 'debit' ? 'Debit' : 'Credit'),
                      subtitle: Column(
                        mainAxisAlignment: MainAxisAlignment.start,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Amount: ₹${transaction['amount']}'),
                          if (transaction['type'] == 'credit')
                            Text('From: ${transaction['senderAccountNumber']}'),
                        ],
                      ),
                      trailing: Text(
                          '${transaction['timestamp'].toDate().toString()}'),
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}