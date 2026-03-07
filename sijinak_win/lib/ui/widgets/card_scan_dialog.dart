import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/providers.dart';
import '../../data/hikvision/alert_stream.dart';

/// Dialog that listens for card tap via the shared HikvisionService.
/// Only accepts events with device time > baseline device time + 2s.
class CardScanDialog extends ConsumerStatefulWidget {
  const CardScanDialog({super.key});

  @override
  ConsumerState<CardScanDialog> createState() => _CardScanDialogState();
}

class _CardScanDialogState extends ConsumerState<CardScanDialog> {
  StreamSubscription? _sub;
  StreamSubscription? _statusSub;
  bool _manualMode = false;
  bool _connected = false;
  final _manualCtrl = TextEditingController();

  /// Only accept events with device time after this cutoff.
  late final DateTime _cutoff;

  @override
  void initState() {
    super.initState();
    final service = ref.read(hikvisionServiceProvider);
    _connected = service.currentStatus == AlertStreamStatus.connected;

    // Baseline = last known device time + 2 seconds
    final baseline = service.lastDeviceTime ?? DateTime(2000);
    _cutoff = baseline.add(const Duration(seconds: 2));

    print('[CardScan] cutoff=$_cutoff connected=$_connected');

    _statusSub = service.status.listen((s) {
      if (!mounted || _manualMode) return;
      setState(() => _connected = s == AlertStreamStatus.connected);
    });

    _sub = service.events.listen((event) {
      if (!mounted || _manualMode) return;
      if (event.cardNo.isEmpty) return;
      if (!event.dateTime.isAfter(_cutoff)) return;

      print('[CardScan] GOT CARD: ${event.cardNo} time=${event.dateTime}');
      Navigator.of(context).pop(event.cardNo);
    });
  }

  void _switchToManual() {
    _sub?.cancel();
    _statusSub?.cancel();
    setState(() => _manualMode = true);
  }

  @override
  void dispose() {
    _sub?.cancel();
    _statusSub?.cancel();
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
          Text(
            _connected
                ? 'Tap kartu pada reader...'
                : 'Menghubungkan ke reader...',
            textAlign: TextAlign.center,
          ),
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
