import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

class AdminPage extends StatefulWidget {
  const AdminPage({Key? key}) : super(key: key);

  @override
  AdminPageState createState() => AdminPageState();
}

class AdminPageState extends State<AdminPage>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
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
        title: const Text('Admin Dashboard'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Unverified Users'),
            Tab(text: 'Verified Users'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildUsersList(isVerified: false),
          _buildUsersList(isVerified: true),
        ],
      ),
    );
  }

  Widget _buildUsersList({required bool isVerified}) {
    return FutureBuilder<List<DocumentSnapshot>>(
      future: _fetchUsers(isVerified),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        } else if (snapshot.hasError) {
          return Center(child: Text('Error: ${snapshot.error}'));
        } else if (snapshot.data!.isEmpty) {
          return const Center(child: Text('No users found.'));
        } else {
          List<DocumentSnapshot> users = snapshot.data!;
          return Padding(
            padding: const EdgeInsets.all(8.0),
            child: ListView.builder(
              itemCount: users.length,
              itemBuilder: (context, index) {
                var userData = users[index].data() as Map<String, dynamic>;
                bool isUserVerified = userData['userRoleVerified'] ?? false;
                return Card(
                  elevation: 4,
                  margin:
                      const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
                  child: ListTile(
                    title: Text(userData['userName'] ?? ''),
                    subtitle: Text(userData['userRole'] ?? ''),
                    trailing: IconButton(
                      onPressed: () {
                        _toggleVerification(
                            userData['userId'] ?? '', isUserVerified);
                      },
                      icon: Icon(isUserVerified ? Icons.check : Icons.clear),
                    ),
                  ),
                );
              },
            ),
          );
        }
      },
    );
  }

  Future<List<DocumentSnapshot>> _fetchUsers(bool isVerified) async {
    QuerySnapshot querySnapshot = await FirebaseFirestore.instance
        .collection('securebankUsers')
        .where('userRoleVerified', isEqualTo: isVerified)
        .get();
    return querySnapshot.docs;
  }

  Future<void> _toggleVerification(
      String userId, bool currentVerificationStatus) async {
    await FirebaseFirestore.instance
        .collection('securebankUsers')
        .doc(userId)
        .update({'userRoleVerified': !currentVerificationStatus});
    setState(() {});
  }
}
