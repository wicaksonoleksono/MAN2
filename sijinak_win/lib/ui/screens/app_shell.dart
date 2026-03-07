import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/providers.dart';
import 'dashboard.dart';
import 'students_screen.dart';
import 'absensi_screen.dart';

class AppShell extends ConsumerStatefulWidget {
  const AppShell({super.key});

  @override
  ConsumerState<AppShell> createState() => _AppShellState();
}

class _AppShellState extends ConsumerState<AppShell> {
  int _selectedIndex = 0;

  static const _destinations = [
    NavigationRailDestination(
      icon: Icon(Icons.dashboard_outlined),
      selectedIcon: Icon(Icons.dashboard),
      label: Text('Dashboard'),
    ),
    NavigationRailDestination(
      icon: Icon(Icons.people_outlined),
      selectedIcon: Icon(Icons.people),
      label: Text('Siswa'),
    ),
    NavigationRailDestination(
      icon: Icon(Icons.fact_check_outlined),
      selectedIcon: Icon(Icons.fact_check),
      label: Text('Absensi'),
    ),
  ];

  bool _hikStarted = false;

  void _ensureHikvisionStarted() {
    if (_hikStarted) return;
    final config = ref.read(configProvider).valueOrNull;
    if (config != null && config.isHikvisionConfigured) {
      ref.read(hikvisionServiceProvider).start(config);
      final attendance = ref.read(attendanceServiceProvider);
      attendance.onTapRecorded = (record, student) {
        // Refresh dashboard data when a tap is recorded
        ref.invalidate(recentRecordsProvider);
        ref.invalidate(pendingSyncCountProvider);
      };
      attendance.start();
      _hikStarted = true;
    }
  }

  @override
  Widget build(BuildContext context) {
    // Start HikvisionService + AttendanceService when config becomes available
    ref.listen(configProvider, (_, next) {
      if (_hikStarted) return;
      final config = next.valueOrNull;
      if (config != null && config.isHikvisionConfigured) {
        _ensureHikvisionStarted();
      }
    });
    _ensureHikvisionStarted();

    final colors = Theme.of(context).colorScheme;

    return Scaffold(
      body: Row(
        children: [
          NavigationRail(
            selectedIndex: _selectedIndex,
            onDestinationSelected: (i) => setState(() => _selectedIndex = i),
            labelType: NavigationRailLabelType.all,
            destinations: _destinations,
            backgroundColor: colors.surfaceContainerLow,
            indicatorColor: colors.primaryContainer,
          ),
          VerticalDivider(thickness: 1, width: 1, color: colors.outlineVariant),
          Expanded(
            child: IndexedStack(
              index: _selectedIndex,
              children: const [
                DashboardScreen(),
                StudentsScreen(),
                AbsensiScreen(),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
