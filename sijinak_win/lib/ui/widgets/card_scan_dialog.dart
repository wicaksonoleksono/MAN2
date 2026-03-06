import 'dart:async';
import 'package:flutter/material.dart';
import '../../config/app_config.dart';
import '../../data/hikvision/isapi_client.dart';
import '../../data/hikvision/alert_stream.dart';

/// Dialog that listens for the next card tap OR allows manual entry.
class CardScanDialog extends StatefulWidget {
  final AppConfig config;
  const CardScanDialog({super.key, required this.config});

  @override
  State<CardScanDialog> createState() => _CardScanDialogState();
}

class _CardScanDialogState extends State<CardScanDialog> {
  AlertStream? _alertStream;
  StreamSubscription? _sub;
  String _status = 'Menghubungkan ke reader...';
  bool _connected = false;
  bool _manualMode = false;
  final _manualCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    _startScan();
  }

  void _startScan() {
    final client = IsapiClient(
      baseUrl: widget.config.hikvisionBaseUrl,
      username: widget.config.hikvisionUser,
      password: widget.config.hikvisionPassword,
    );
    _alertStream = AlertStream(client: client);

    _alertStream!.status.listen((s) {
      if (!mounted || _manualMode) return;
      setState(() {
        _connected = s == AlertStreamStatus.connected;
        _status = switch (s) {
          AlertStreamStatus.connecting => 'Menghubungkan ke reader...',
          AlertStreamStatus.connected => 'Tap kartu pada reader...',
          AlertStreamStatus.disconnected => 'Terputus, mencoba ulang...',
        };
      });
    });

    _sub = _alertStream!.events.listen((event) {
      Navigator.of(context).pop(event.cardNo);
    });

    _alertStream!.start();
  }

  void _switchToManual() {
    _sub?.cancel();
    _alertStream?.dispose();
    _alertStream = null;
    setState(() => _manualMode = true);
  }

  @override
  void dispose() {
    _sub?.cancel();
    _alertStream?.dispose();
    _manualCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    if (_manualMode) {
      return AlertDialog(
        title: const Text('Input Kartu Manual'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: _manualCtrl,
              autofocus: true,
              decoration: const InputDecoration(
                labelText: 'Nomor Kartu',
                hintText: 'Contoh: 12345678',
                border: OutlineInputBorder(),
              ),
              onSubmitted: (v) {
                final val = v.trim();
                if (val.isNotEmpty) Navigator.of(context).pop(val);
              },
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(null),
            child: const Text('Batal'),
          ),
          FilledButton(
            onPressed: () {
              final val = _manualCtrl.text.trim();
              if (val.isNotEmpty) Navigator.of(context).pop(val);
            },
            child: const Text('Simpan'),
          ),
        ],
      );
    }

    return AlertDialog(
      title: const Text('Assign Kartu'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            _connected ? Icons.contactless : Icons.sensors,
            size: 64,
            color: _connected ? colors.primary : colors.outline,
          ),
          const SizedBox(height: 16),
          if (!_connected)
            const SizedBox(
              width: 24,
              height: 24,
              child: CircularProgressIndicator(strokeWidth: 2),
            ),
          const SizedBox(height: 8),
          Text(_status, textAlign: TextAlign.center),
          const SizedBox(height: 16),
          TextButton.icon(
            onPressed: _switchToManual,
            icon: const Icon(Icons.keyboard, size: 18),
            label: const Text('Input manual'),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(null),
          child: const Text('Batal'),
        ),
      ],
    );
  }
}
