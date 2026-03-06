import 'dart:convert';
import 'dart:io';

import '../../config/app_config.dart';

class ApiClient {
  final String baseUrl;
  final String apiKey;

  ApiClient({required this.baseUrl, required this.apiKey});

  factory ApiClient.fromConfig(AppConfig config) =>
      ApiClient(baseUrl: config.serverUrl, apiKey: config.apiKey);

  Future<List<Map<String, dynamic>>> fetchStudents() async {
    final client = HttpClient();
    client.connectionTimeout = const Duration(seconds: 15);
    try {
      final request = await client.getUrl(
        Uri.parse('$baseUrl/api/desktop/students'),
      );
      request.headers.set('X-API-Key', apiKey);
      final response = await request.close();
      final body = await response.transform(utf8.decoder).join();

      if (response.statusCode == 401 || response.statusCode == 403) {
        throw ApiException('Invalid API key', response.statusCode);
      }
      if (response.statusCode != 200) {
        throw ApiException('HTTP ${response.statusCode}', response.statusCode);
      }

      final list = jsonDecode(body) as List;
      return list.cast<Map<String, dynamic>>();
    } finally {
      client.close();
    }
  }
}

class ApiException implements Exception {
  final String message;
  final int statusCode;
  ApiException(this.message, this.statusCode);

  @override
  String toString() => 'ApiException($statusCode): $message';
}
