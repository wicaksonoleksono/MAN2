import 'dart:async';
import 'package:flutter/material.dart';
import '../../config/app_config.dart';
import '../../data/local/database.dart';
import '../../services/student_service.dart';

/// Dialog that pushes students to Hikvision one-by-one with progress.
class BulkPushDialog extends StatefulWidget {
  final List<Student> students;
  final AppConfig config;
  final AppDatabase db;

  const BulkPushDialog({
    super.key,
    required this.students,
    required this.config,
    required this.db,
  });

  @override
  State<BulkPushDialog> createState() => _BulkPushDialogState();
}

class _BulkPushDialogState extends State<BulkPushDialog> {
  BulkPushProgress _progress = const BulkPushProgress(
    current: 0,
    total: 0,
    currentName: '',
    success: 0,
    failed: 0,
    done: false,
  );
  StreamSubscription? _sub;

  @override
  void initState() {
    super.initState();
    _run();
  }

  void _run() {
    final service = StudentService(widget.db);
    _sub = service
        .pushBulk(widget.students, widget.config)
        .listen((progress) {
      if (mounted) setState(() => _progress = progress);
    });
  }

  @override
  void dispose() {
    _sub?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final total = widget.students.length;
    final progress = total > 0 ? _progress.current / total : 0.0;

    return AlertDialog(
      title: Text(_progress.done ? 'Selesai' : 'Mendaftarkan ke Hikvision...'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          LinearProgressIndicator(value: progress),
          const SizedBox(height: 16),
          Text(
            _progress.done
                ? '${_progress.success} berhasil, ${_progress.failed} gagal'
                : '${_progress.current} / $total — ${_progress.currentName}',
            textAlign: TextAlign.center,
          ),
          if (_progress.lastError != null && _progress.done) ...[
            const SizedBox(height: 8),
            Text(
              'Error terakhir: ${_progress.lastError}',
              style: TextStyle(
                  fontSize: 11, color: Theme.of(context).colorScheme.error),
            ),
          ],
        ],
      ),
      actions: [
        if (_progress.done)
          FilledButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Tutup'),
          ),
      ],
    );
  }
}
