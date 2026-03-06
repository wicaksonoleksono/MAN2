import 'dart:convert';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as p;

class AppConfig {
  String hikvisionIp;
  String hikvisionUser;
  String hikvisionPassword;
  String serverUrl;
  String apiKey;
  String frontendUrl;

  AppConfig({
    this.hikvisionIp = '192.168.40.181',
    this.hikvisionUser = 'admin',
    this.hikvisionPassword = '',
    this.serverUrl = 'http://localhost:2385',
    this.apiKey = '',
    this.frontendUrl = 'http://localhost:4923',
  });

  String get hikvisionBaseUrl => 'http://$hikvisionIp';

  bool get isHikvisionConfigured =>
      hikvisionIp.isNotEmpty && hikvisionPassword.isNotEmpty;

  bool get isServerConfigured =>
      serverUrl.isNotEmpty && apiKey.isNotEmpty;

  static Future<File> get _configFile async {
    final dir = await getApplicationSupportDirectory();
    return File(p.join(dir.path, 'config.json'));
  }

  static Future<AppConfig> load() async {
    try {
      final file = await _configFile;
      if (await file.exists()) {
        final json = jsonDecode(await file.readAsString()) as Map<String, dynamic>;
        return AppConfig(
          hikvisionIp: json['hikvision_ip'] as String? ?? '192.168.40.181',
          hikvisionUser: json['hikvision_user'] as String? ?? 'admin',
          hikvisionPassword: json['hikvision_password'] as String? ?? '',
          serverUrl: json['server_url'] as String? ?? 'http://localhost:2385',
          apiKey: json['api_key'] as String? ?? '',
          frontendUrl: json['frontend_url'] as String? ?? 'http://localhost:4923',
        );
      }
    } catch (_) {}
    return AppConfig();
  }

  Future<void> save() async {
    final file = await _configFile;
    await file.parent.create(recursive: true);
    await file.writeAsString(const JsonEncoder.withIndent('  ').convert({
      'hikvision_ip': hikvisionIp,
      'hikvision_user': hikvisionUser,
      'hikvision_password': hikvisionPassword,
      'server_url': serverUrl,
      'api_key': apiKey,
      'frontend_url': frontendUrl,
    }));
  }
}
