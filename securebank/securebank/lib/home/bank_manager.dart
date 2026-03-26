import 'dart:io';

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:open_file/open_file.dart';
import 'package:path_provider/path_provider.dart';
import 'package:securebank/home/account_list.dart';
import 'package:securebank/home/deposit.dart';
import 'package:securebank/home/transactions.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;

class BankManagerPage extends StatelessWidget {
  const BankManagerPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Bank Manager'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Welcome to Bank Manager',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 20),
            ElevatedButton.icon(
              onPressed: () {
                // Navigate to deposit page
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => DepositMoneyPage()),
                );
              },
              icon: Icon(Icons.money),
              label: Text('Deposit Amount'),
            ),
            SizedBox(height: 20),
            ElevatedButton.icon(
              onPressed: () {
                // Navigate to account list page
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => AccountListPage()),
                );
              },
              icon: Icon(Icons.account_balance),
              label: Text('View Accounts'),
            ),
            SizedBox(height: 20),
            ElevatedButton.icon(
              onPressed: () {
                // Navigate to transaction management page
                Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (context) => TransactionManagementPage()),
                );
              },
              icon: Icon(Icons.list),
              label: Text('Manage Transactions'),
            ),
            SizedBox(height: 20),
            ElevatedButton.icon(
              onPressed: () async {
                // Fetch transactions from Firestore
                List<Map<String, dynamic>> transactions =
                    await fetchTransactionsFromFirestore();

                // Generate PDF report
                await generatePDFReport(transactions);
              },
              icon: Icon(Icons.bar_chart),
              label: Text('Generate Reports'),
            ),
            SizedBox(height: 20),
            ElevatedButton.icon(
              onPressed: () {
                // Sign out functionality
                FirebaseAuth.instance.signOut();
              },
              icon: Icon(Icons.logout),
              label: Text('Sign Out'),
            ),
          ],
        ),
      ),
    );
  }

  Future<List<Map<String, dynamic>>> fetchTransactionsFromFirestore() async {
    // Perform a query to get the transaction data from Firestore
    QuerySnapshot<Map<String, dynamic>> querySnapshot =
        await FirebaseFirestore.instance.collection('transactions').get();

    // Convert QuerySnapshot to a list of Map<String, dynamic>
    List<Map<String, dynamic>> transactions = [];
    querySnapshot.docs.forEach((doc) {
      transactions.add(doc.data());
    });

    return transactions;
  }

  Future<void> generatePDFReport(
      List<Map<String, dynamic>> transactions) async {
    final pdf = pw.Document();

    // Add title to the PDF
    pdf.addPage(
      pw.Page(
        build: (context) {
          return pw.Center(
            child: pw.Text('Transaction Report',
                style:
                    pw.TextStyle(fontSize: 24, fontWeight: pw.FontWeight.bold)),
          );
        },
      ),
    );

    // Add transaction data to the PDF
    transactions.forEach((transaction) {
      pdf.addPage(
        pw.Page(
          build: (context) {
            return pw.Column(
              crossAxisAlignment: pw.CrossAxisAlignment.start,
              children: [
                pw.Text('Sender ID: ${transaction['senderId']}'),
                pw.Text('Recipient ID: ${transaction['recipientId']}'),
                pw.Text('Amount: ₹${transaction['amount']}'),
                pw.Text('Timestamp: ${transaction['timestamp'].toDate()}'),
                pw.SizedBox(height: 20),
              ],
            );
          },
        ),
      );
    });

    // Save the PDF to a file
    final output = await getTemporaryDirectory();
    final file = File('${output.path}/transaction_report.pdf');
    await file.writeAsBytes(await pdf.save());

    // Open the PDF using a PDF viewer
    OpenFile.open(file.path);
  }
}
