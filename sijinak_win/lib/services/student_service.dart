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

  /// Assign a card to a student on both Hikvision and local DB.
  Future<void> assignCard(Student student, String cardNo, AppConfig config) async {
    final hikId = student.userId.replaceAll('-', '');
    print('[assignCard] userId=${student.userId} hikId=$hikId cardNo=$cardNo');

    final client = IsapiClient(
      baseUrl: config.hikvisionBaseUrl,
      username: config.hikvisionUser,
      password: config.hikvisionPassword,
    );

    print('[assignCard] upserting person...');
    await client.upsertPerson(
      employeeNo: student.userId,
      name: student.nama,
    );
    print('[assignCard] person OK, upserting card...');

    await client.upsertCard(
      cardNo: cardNo,
      employeeNo: student.userId,
    );
    print('[assignCard] card OK, saving to DB...');

    await db.assignCardToStudent(student.userId, cardNo);
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
