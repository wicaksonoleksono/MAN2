import 'dart:async';
import 'package:drift/drift.dart';
import '../data/local/database.dart';
import '../data/hikvision/hik_event.dart';
import 'hikvision_service.dart';

/// Listens to the shared HikvisionService event stream and records
/// attendance (tap in / tap out) for known cards.
class AttendanceService {
  final AppDatabase db;
  final HikvisionService hikService;

  StreamSubscription? _sub;
  bool _running = false;

  /// Callback fired when a new tap record is inserted.
  void Function(TapRecord record, Student student)? onTapRecorded;

  AttendanceService({required this.db, required this.hikService});

  void start() {
    if (_running) return;
    _running = true;
    _sub = hikService.events.listen(_handleEvent);
  }

  void stop() {
    _running = false;
    _sub?.cancel();
    _sub = null;
  }

  /// Convert Hikvision employeeNo (32 hex, no hyphens) back to UUID format.
  String _toUuid(String employeeNo) {
    final h = employeeNo;
    if (h.length != 32) return employeeNo;
    return '${h.substring(0, 8)}-${h.substring(8, 12)}-${h.substring(12, 16)}'
        '-${h.substring(16, 20)}-${h.substring(20)}';
  }

  Future<void> _handleEvent(HikEvent event) async {
    if (event.cardNo.isEmpty) return;

    // Look up student: prefer employeeNo (device already validated the card)
    Student? student;
    if (event.employeeNo != null && event.employeeNo!.isNotEmpty) {
      final userId = _toUuid(event.employeeNo!);
      student = await db.getStudentByUserId(userId);
    }
    // Fallback to cardNo lookup
    student ??= await db.getStudentByCard(event.cardNo);
    if (student == null) return; // unknown card, ignore

    // Determine masuk or keluar based on today's tap count
    final todayTaps = await db.getTodayRecordsForCard(event.cardNo);
    final eventType = todayTaps.isEmpty ? 'absen_masuk' : 'absen_keluar';

    final now = DateTime.now().millisecondsSinceEpoch ~/ 1000;
    final recordId = '${event.cardNo}_${event.serialNo}';

    final companion = TapRecordsCompanion(
      id: Value(recordId),
      cardNo: Value(event.cardNo),
      eventType: Value(eventType),
      deviceTime: Value(event.dateTime.millisecondsSinceEpoch ~/ 1000),
      hikSerialNo: Value(event.serialNo),
      createdAt: Value(now),
    );

    final inserted = await db.insertTapRecord(companion);
    if (inserted > 0) {
      onTapRecorded?.call(
        TapRecord(
          id: recordId,
          cardNo: event.cardNo,
          eventType: eventType,
          deviceTime: event.dateTime.millisecondsSinceEpoch ~/ 1000,
          hikSerialNo: event.serialNo,
          createdAt: now,
          reason: null,
          publishedAt: null,
        ),
        student,
      );
    }
  }
}
