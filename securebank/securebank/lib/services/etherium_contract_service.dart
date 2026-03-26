import 'dart:convert';
import 'package:http/http.dart' as http;

class EthereumContractService {
  String baseUrl = 'http://192.168.186.228:5000';

  Future<Map<String, dynamic>> addTransactionToBlockchain(
      String transactionType,
      int amount,
      String recipientAccountNumber,
      String senderId) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/addTransactionToBlockchain'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'transactionType': transactionType,
          'amount': amount,
          'recipientAccountNumber': recipientAccountNumber,
          'senderId': senderId,
        }),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to add transaction to blockchain');
      }
    } catch (error) {
      print('Error adding transaction to blockchain: $error');
      return {
        'status': 'error',
        'message': 'Error adding transaction to blockchain'
      };
    }
  }
}
