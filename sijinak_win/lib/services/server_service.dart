import 'dart:io';

/// Result of a server connection test.
class ServerTestResult {
  final bool success;
  final String message;
  final String? errorField; // 'url' or 'key'

  const ServerTestResult({
    required this.success,
    required this.message,
    this.errorField,
  });
}

class ServerService {
  /// Test server connection with the given URL and API key.
  static Future<ServerTestResult> testConnection(String url, String apiKey) async {
    try {
      final client = HttpClient();
      client.connectionTimeout = const Duration(seconds: 10);
      try {
        final request = await client.getUrl(
          Uri.parse('$url/api/desktop/settings'),
        );
        request.headers.set('X-API-Key', apiKey);
        final response = await request.close();
        await response.drain<void>();

        if (response.statusCode == 200) {
          return const ServerTestResult(success: true, message: 'Connected to server');
        } else if (response.statusCode == 401 || response.statusCode == 403) {
          return const ServerTestResult(
            success: false,
            message: 'Invalid API key',
            errorField: 'key',
          );
        } else {
          return ServerTestResult(
            success: false,
            message: 'Server responded with ${response.statusCode}',
            errorField: 'url',
          );
        }
      } finally {
        client.close();
      }
    } catch (e) {
      String msg = e.toString();
      if (msg.contains('Connection refused') ||
          msg.contains('SocketException') ||
          msg.contains('No route to host')) {
        msg = 'Cannot reach server — check URL';
      } else if (msg.contains('timed out') ||
          msg.contains('TimeoutException')) {
        msg = 'Connection timed out';
      } else if (msg.contains('FormatException') ||
          msg.contains('Invalid URI')) {
        msg = 'Invalid URL format';
      }
      return ServerTestResult(success: false, message: msg, errorField: 'url');
    }
  }
}
