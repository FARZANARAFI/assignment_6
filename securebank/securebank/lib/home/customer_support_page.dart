import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';

class CustomerSupportPage extends StatefulWidget {
  const CustomerSupportPage({Key? key}) : super(key: key);

  @override
  State<CustomerSupportPage> createState() => _CustomerSupportPageState();
}

class _CustomerSupportPageState extends State<CustomerSupportPage> {
  String _chatMessage = '';

  // Function to handle sending a message in the chat
  void _sendMessage(String message) {
    // Implement sending message logic here
    // For simplicity, just updating the message locally
    setState(() {
      _chatMessage = message;
    });
  }

  // Function to make a call to the support helpline
  void _callSupportHelpline() {
    // Implement calling support helpline logic here
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        actions: [
          IconButton(
              onPressed: () {
                FirebaseAuth.instance.signOut();
              },
              icon: Icon(Icons.logout))
        ],
        title: Text('Customer Support'),
      ),
      body: Column(
        children: [
          // Widget for displaying chat messages
          Expanded(
            child: ListView(
              children: [
                // Display chat messages here
                ListTile(
                  title: Text(_chatMessage),
                ),
              ],
            ),
          ),
          // Input field for sending messages in the chat
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    onChanged: (value) {
                      _sendMessage(value);
                    },
                    decoration: InputDecoration(
                      hintText: 'Type your message here...',
                    ),
                  ),
                ),
                IconButton(
                  icon: Icon(Icons.send),
                  onPressed: () {
                    // Logic to send message
                    _sendMessage(_chatMessage);
                  },
                ),
              ],
            ),
          ),
          // Button for calling support helpline
          ElevatedButton(
            onPressed: () {
              // Logic to call support helpline
              _callSupportHelpline();
            },
            child: Text('Call Support Helpline'),
          ),
        ],
      ),
    );
  }
}
