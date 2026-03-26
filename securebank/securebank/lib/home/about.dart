import 'package:flutter/material.dart';
import 'package:lottie/lottie.dart';

class AboutPage extends StatelessWidget {
  const AboutPage({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(20.0),
      children: [
        const SizedBox(
          height: 60,
        ),
        Lottie.asset('assets/images/about.json'),
        const Center(
          child: Text(
            'About Us',
            style: TextStyle(fontSize: 30),
          ),
        ),
        const SizedBox(
          height: 10,
        ),
        _buildMemberCard(
          name: 'Ahmed Rameez',
          email: 'ahmedrameez2010@gmail.com',
          avatarColor: Colors.orange,
        ),
        const SizedBox(height: 5),
        _buildMemberCard(
          name: 'Frentzen Benny',
          email: 'frentzenbenny@gmail.com',
          avatarColor: Colors.green,
        ),
        const SizedBox(height: 5),
        _buildMemberCard(
          name: 'Noel Jacob',
          email: 'noel@gmail.com',
          avatarColor: Colors.blue,
        ),
        const SizedBox(height: 5),
        _buildMemberCard(
          name: 'Riya',
          email: 'riyaang@gmail.com',
          avatarColor: Colors.red,
        ),
      ],
    );
  }

  Widget _buildMemberCard({
    required String name,
    required String email,
    required Color avatarColor,
  }) {
    return Card(
      elevation: 5,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(15.0),
      ),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: avatarColor,
          child: Text(
            name.substring(0, 1),
            style: const TextStyle(color: Colors.white),
          ),
        ),
        title: Text(
          name,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 18,
          ),
        ),
        subtitle: Text(email),
      ),
    );
  }
}
