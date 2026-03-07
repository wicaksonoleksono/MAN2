import '../config/app_config.dart';
import '../data/local/database.dart';
import '../data/hikvision/isapi_client.dart';

/// Result of a bulk push operation, emitted per-student.
class BulkPushProgress {
  final int current;
  final int total;
  final String currentName;
  final int success;
  final int failed;
  final bool done;
  final String? lastError;

  const BulkPushProgress({
    required this.current,
    required this.total,
    required this.currentName,
    required this.success,
    required this.failed,
    required this.done,
    this.lastError,
  });
}

class CardAlreadyAssignedException implements Exception {
  final String cardNo;
  final String ownerName;
  CardAlreadyAssignedException(this.cardNo, this.ownerName);

  @override
  String toString() => 'Kartu $cardNo sudah dipakai oleh $ownerName';
}

class StudentService {
  final AppDatabase db;

  StudentService(this.db);

  Future<List<Student>> loadStudents() => db.getAllStudents();

  Future<List<Student>> getUnregistered() => db.getUnregisteredStudents();

  /// Push a single student to Hikvision and mark as registered.
  Future<void> pushToHikvision(Student student, AppConfig config) async {
    final client = IsapiClient(
      baseUrl: config.hikvisionBaseUrl,
      username: config.hikvisionUser,
      password: config.hikvisionPassword,
    );
    await client.upsertPerson(
      employeeNo: student.userId,
      name: student.nama,
    );
    await db.markHikRegistered(student.userId);
  }

  /// Check if card is already assigned to another student.
  /// Returns the owner if duplicate, null if available.
  Future<Student?> checkCardDuplicate(String cardNo, String excludeUserId) async {
    final existing = await db.getStudentByCard(cardNo);
    if (existing != null && existing.userId != excludeUserId) {
      return existing;
    }
    return null;
  }

  /// Assign a card to a student on both Hikvision and local DB.
  /// Throws [CardAlreadyAssignedException] if card belongs to another student.
  Future<void> assignCard(Student student, String cardNo, AppConfig config) async {
    // Check for duplicate in local DB
    final existing = await checkCardDuplicate(cardNo, student.userId);
    if (existing != null) {
      throw CardAlreadyAssignedException(cardNo, existing.nama);
    }

    final client = IsapiClient(
      baseUrl: config.hikvisionBaseUrl,
      username: config.hikvisionUser,
      password: config.hikvisionPassword,
    );

    // Only register person if not already on device
    if (!student.hikRegistered) {
      print('[assignCard] registering person ${student.userId}');
      await client.upsertPerson(
        employeeNo: student.userId,
        name: student.nama,
      );
      await db.markHikRegistered(student.userId);
      print('[assignCard] person registered');
    } else {
      print('[assignCard] person already registered, skipping');
    }

    print('[assignCard] assigning card $cardNo to ${student.userId}');
    await client.upsertCard(
      cardNo: cardNo,
      employeeNo: student.userId,
    );
    print('[assignCard] card assigned on device');
    await db.assignCardToStudent(student.userId, cardNo);
    print('[assignCard] card saved to DB');
  }

  /// Remove card from student (local DB + Hikvision).
  Future<void> removeCard(Student student, AppConfig config) async {
    if (student.cardNo == null) return;

    if (config.isHikvisionConfigured) {
      try {
        final client = IsapiClient(
          baseUrl: config.hikvisionBaseUrl,
          username: config.hikvisionUser,
          password: config.hikvisionPassword,
        );
        await client.deleteCard(cardNo: student.cardNo!);
      } catch (_) {
        // Card might not exist on device, continue anyway
      }
    }

    await db.removeCardFromStudent(student.userId);
  }

  /// Push unregistered students one-by-one, yielding progress.
  Stream<BulkPushProgress> pushBulk(List<Student> students, AppConfig config) async* {
    final client = IsapiClient(
      baseUrl: config.hikvisionBaseUrl,
      username: config.hikvisionUser,
      password: config.hikvisionPassword,
    );

    int success = 0;
    int failed = 0;
    String? lastError;

    for (int i = 0; i < students.length; i++) {
      final s = students[i];
      yield BulkPushProgress(
        current: i + 1,
        total: students.length,
        currentName: s.nama,
        success: success,
        failed: failed,
        done: false,
      );

      try {
        await client.upsertPerson(employeeNo: s.userId, name: s.nama);
        await db.markHikRegistered(s.userId);
        success++;
      } catch (e) {
        failed++;
        lastError = e.toString();
      }
    }

    yield BulkPushProgress(
      current: students.length,
      total: students.length,
      currentName: '',
      success: success,
      failed: failed,
      done: true,
      lastError: lastError,
    );
  }
}
