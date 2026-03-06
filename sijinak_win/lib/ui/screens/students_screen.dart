import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/local/database.dart';
import '../../providers/providers.dart';
import '../widgets/card_scan_dialog.dart';
import '../widgets/bulk_push_dialog.dart';

class StudentsScreen extends ConsumerStatefulWidget {
  const StudentsScreen({super.key});

  @override
  ConsumerState<StudentsScreen> createState() => _StudentsScreenState();
}

class _StudentsScreenState extends ConsumerState<StudentsScreen> {
  List<Student> _students = [];
  List<Student> _filtered = [];
  final _searchCtrl = TextEditingController();
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadStudents();
    _searchCtrl.addListener(_applyFilter);
  }

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadStudents() async {
    final students = await ref.read(studentServiceProvider).loadStudents();
    if (mounted) {
      setState(() {
        _students = students;
        _loading = false;
        _applyFilter();
      });
    }
  }

  void _applyFilter() {
    final q = _searchCtrl.text.trim().toLowerCase();
    setState(() {
      if (q.isEmpty) {
        _filtered = _students;
      } else {
        _filtered = _students.where((s) {
          return s.nama.toLowerCase().contains(q) ||
              (s.nis?.toLowerCase().contains(q) ?? false) ||
              (s.kelas?.toLowerCase().contains(q) ?? false) ||
              (s.cardNo?.toLowerCase().contains(q) ?? false);
        }).toList();
      }
    });
  }

  Future<void> _syncAndReload() async {
    setState(() => _loading = true);
    await ref.read(studentSyncProvider.notifier).syncStudents();
    await _loadStudents();
  }

  Future<void> _pushAllToHikvision() async {
    final config = ref.read(configProvider).valueOrNull;
    if (config == null || !config.isHikvisionConfigured) {
      _showSnack('Konfigurasi Hikvision belum lengkap');
      return;
    }

    final unregistered = await ref.read(studentServiceProvider).getUnregistered();

    if (unregistered.isEmpty) {
      _showSnack('Semua siswa sudah terdaftar di Hikvision');
      return;
    }

    if (!mounted) return;

    await showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => BulkPushDialog(
        students: unregistered,
        config: config,
        db: ref.read(databaseProvider),
      ),
    );

    await _loadStudents();
  }

  Future<void> _pushOneToHikvision(Student student) async {
    final config = ref.read(configProvider).valueOrNull;
    if (config == null || !config.isHikvisionConfigured) {
      _showSnack('Konfigurasi Hikvision belum lengkap');
      return;
    }
    try {
      await ref.read(studentServiceProvider).pushToHikvision(student, config);
      _showSnack('${student.nama} berhasil didaftarkan ke Hikvision');
      await _loadStudents();
    } catch (e) {
      _showSnack('Gagal: $e');
    }
  }

  Future<void> _assignCard(Student student) async {
    final config = ref.read(configProvider).valueOrNull;
    if (config == null || !config.isHikvisionConfigured) {
      _showSnack('Konfigurasi Hikvision belum lengkap');
      return;
    }

    final result = await showDialog<String>(
      context: context,
      barrierDismissible: false,
      builder: (_) => CardScanDialog(config: config),
    );

    if (result == null || !mounted) return;

    try {
      await ref.read(studentServiceProvider).assignCard(student, result, config);
      _showSnack('Kartu $result berhasil di-assign ke ${student.nama}');
      await _loadStudents();
    } catch (e) {
      _showSnack('Gagal assign kartu: $e');
    }
  }

  void _showSnack(String msg) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colors = theme.colorScheme;
    final syncState = ref.watch(studentSyncProvider);

    return Column(
      children: [
        // Header
        Container(
          padding: const EdgeInsets.fromLTRB(24, 20, 16, 12),
          decoration: BoxDecoration(
            color: colors.surface,
            border: Border(
              bottom: BorderSide(color: colors.outlineVariant, width: 1),
            ),
          ),
          child: Column(
            children: [
              Row(
                children: [
                  Icon(Icons.people, color: colors.primary, size: 24),
                  const SizedBox(width: 10),
                  Text('Daftar Siswa',
                      style: theme.textTheme.titleLarge
                          ?.copyWith(fontWeight: FontWeight.w600)),
                  const Spacer(),
                  Text(
                    '${_filtered.length} siswa',
                    style: theme.textTheme.bodySmall
                        ?.copyWith(color: colors.outline),
                  ),
                  const SizedBox(width: 4),
                  IconButton(
                    icon: const Icon(Icons.upload, size: 20),
                    onPressed: _pushAllToHikvision,
                    tooltip: 'Push semua ke Hikvision',
                  ),
                  const SizedBox(width: 4),
                  syncState.when(
                    data: (s) => s.syncing
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : IconButton(
                            icon: const Icon(Icons.sync, size: 20),
                            onPressed: _syncAndReload,
                            tooltip: 'Sync dari server',
                          ),
                    loading: () => const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    ),
                    error: (_, __) => IconButton(
                      icon: const Icon(Icons.sync_problem, size: 20),
                      onPressed: _syncAndReload,
                      tooltip: 'Retry sync',
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _searchCtrl,
                decoration: InputDecoration(
                  hintText: 'Cari nama, NIS, kelas...',
                  prefixIcon: const Icon(Icons.search, size: 20),
                  isDense: true,
                  contentPadding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                    borderSide: BorderSide(color: colors.outlineVariant),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                    borderSide: BorderSide(color: colors.outlineVariant),
                  ),
                  filled: true,
                  fillColor: colors.surfaceContainerLow,
                ),
              ),
            ],
          ),
        ),

        // Body
        Expanded(
          child: _loading
              ? const Center(child: CircularProgressIndicator())
              : _filtered.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.person_off,
                              size: 56, color: colors.outlineVariant),
                          const SizedBox(height: 12),
                          Text(
                            _students.isEmpty
                                ? 'Belum ada data siswa'
                                : 'Tidak ditemukan',
                            style: theme.textTheme.titleMedium
                                ?.copyWith(color: colors.outline),
                          ),
                          if (_students.isEmpty) ...[
                            const SizedBox(height: 4),
                            Text(
                              'Tekan tombol sync untuk mengambil data dari server',
                              style: theme.textTheme.bodySmall
                                  ?.copyWith(color: colors.outlineVariant),
                            ),
                            const SizedBox(height: 16),
                            FilledButton.icon(
                              onPressed: _syncAndReload,
                              icon: const Icon(Icons.sync, size: 18),
                              label: const Text('Sync Siswa'),
                            ),
                          ],
                        ],
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 4),
                      itemCount: _filtered.length,
                      itemBuilder: (context, index) {
                        final s = _filtered[index];
                        return Card(
                          elevation: 0,
                          margin: const EdgeInsets.symmetric(
                              horizontal: 8, vertical: 3),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(10),
                            side: BorderSide(
                                color: colors.outlineVariant.withOpacity(0.5)),
                          ),
                          child: ListTile(
                            leading: CircleAvatar(
                              backgroundColor:
                                  colors.primaryContainer.withOpacity(0.5),
                              child: Text(
                                s.nama.isNotEmpty
                                    ? s.nama[0].toUpperCase()
                                    : '?',
                                style: TextStyle(
                                  color: colors.primary,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                            title: Text(s.nama,
                                style: const TextStyle(
                                    fontWeight: FontWeight.w500)),
                            subtitle: Text(
                              [
                                if (s.nis != null) 'NIS: ${s.nis}',
                                if (s.kelas != null) s.kelas,
                              ].join(' · '),
                              style: TextStyle(
                                  color: colors.onSurfaceVariant,
                                  fontSize: 12),
                            ),
                            trailing: s.cardNo != null
                                ? Chip(
                                    label: Text(s.cardNo!,
                                        style: const TextStyle(fontSize: 11)),
                                    avatar: const Icon(Icons.contactless,
                                        size: 14),
                                    visualDensity: VisualDensity.compact,
                                    padding: EdgeInsets.zero,
                                  )
                                : Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      if (!s.hikRegistered)
                                        IconButton(
                                          icon: Icon(Icons.upload,
                                              size: 18, color: colors.outline),
                                          tooltip: 'Push ke Hikvision',
                                          onPressed: () =>
                                              _pushOneToHikvision(s),
                                        ),
                                      IconButton(
                                        icon: Icon(Icons.add_card,
                                            color: colors.primary),
                                        tooltip: 'Assign kartu',
                                        onPressed: () => _assignCard(s),
                                      ),
                                    ],
                                  ),
                          ),
                        );
                      },
                    ),
        ),
      ],
    );
  }
}
