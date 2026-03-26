import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

class TransactionManagementPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Transaction Management'),
      ),
      body: StreamBuilder(
        stream:
            FirebaseFirestore.instance.collection('transactions').snapshots(),
        builder: (context, AsyncSnapshot<QuerySnapshot> snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return Center(
              child: CircularProgressIndicator(),
            );
          }
          if (snapshot.hasError) {
            return Center(
              child: Text('Error: ${snapshot.error}'),
            );
          }
          if (snapshot.data == null || snapshot.data!.docs.isEmpty) {
            return Center(
              child: Text('No transactions found.'),
            );
          }
          return ListView.builder(
            itemCount: snapshot.data!.docs.length,
            itemBuilder: (context, index) {
              var transaction = snapshot.data!.docs[index];
              return ListTile(
                title: Text('Sender ID: ${transaction['senderId']}'),
                subtitle: Text('Recipient ID: ${transaction['recipientId']}\n'
                    'Amount: ₹${transaction['amount'].toStringAsFixed(2)}\n'
                    'Timestamp: ${transaction['timestamp'].toDate()}'),
              );
            },
          );
        },
      ),
    );
  }
}
