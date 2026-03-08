import 'package:flutter/material.dart';
import '../../data/local/database.dart';

class TapPopupResult {
  final String eventType; // absen_masuk, absen_keluar, izin
  final String? reason;

  const TapPopupResult({required this.eventType, this.reason});
}

class TapPopupDialog extends StatefulWidget {
  final Student student;
  final String suggestedType;

  const TapPopupDialog({
    super.key,
    required this.student,
    required this.suggestedType,
  });

  @override
  State<TapPopupDialog> createState() => _TapPopupDialogState();
}

class _TapPopupDialogState extends State<TapPopupDialog> {
  late String _selected;
  final _keteranganCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    _selected = widget.suggestedType;
  }

  @override
  void dispose() {
    _keteranganCtrl.dispose();
    super.dispose();
  }

  void _confirm() {
    final reason = _selected == 'izin' ? _keteranganCtrl.text.trim() : null;
    Navigator.of(context).pop(TapPopupResult(eventType: _selected, reason: reason));
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colors = theme.colorScheme;
    final student = widget.student;

    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 400),
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Student info
              Row(
                children: [
                  CircleAvatar(
                    radius: 28,
                    backgroundColor: colors.primaryContainer,
                    child: Icon(Icons.person, size: 28, color: colors.primary),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          student.nama,
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          [
                            if (student.nis != null) student.nis!,
                            if (student.kelas != null) student.kelas!,
                          ].join(' · '),
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: colors.onSurfaceVariant,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 24),
              const Divider(height: 1),
              const SizedBox(height: 20),

              // Action buttons — only show the relevant masuk/keluar + izin
              Text(
                'Pilih Jenis Absensi',
                style: theme.textTheme.labelMedium?.copyWith(
                  color: colors.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  if (widget.suggestedType == 'absen_masuk') ...[
                    _ActionButton(
                      label: 'Masuk',
                      icon: Icons.login,
                      color: Colors.green,
                      selected: _selected == 'absen_masuk',
                      onTap: () => setState(() => _selected = 'absen_masuk'),
                    ),
                    const SizedBox(width: 8),
                  ],
                  if (widget.suggestedType == 'absen_keluar') ...[
                    _ActionButton(
                      label: 'Keluar',
                      icon: Icons.logout,
                      color: Colors.blue,
                      selected: _selected == 'absen_keluar',
                      onTap: () => setState(() => _selected = 'absen_keluar'),
                    ),
                    const SizedBox(width: 8),
                  ],
                  _ActionButton(
                    label: 'Izin',
                    icon: Icons.description_outlined,
                    color: Colors.orange,
                    selected: _selected == 'izin',
                    onTap: () => setState(() => _selected = 'izin'),
                  ),
                ],
              ),

              // Keterangan field (izin only)
              if (_selected == 'izin') ...[
                const SizedBox(height: 16),
                TextField(
                  controller: _keteranganCtrl,
                  autofocus: true,
                  maxLines: 2,
                  decoration: InputDecoration(
                    labelText: 'Keterangan',
                    hintText: 'Alasan izin...',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                    isDense: true,
                  ),
                ),
              ],

              const SizedBox(height: 24),

              // Confirm / Cancel
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  TextButton(
                    onPressed: () => Navigator.of(context).pop(null),
                    child: const Text('Batal'),
                  ),
                  const SizedBox(width: 8),
                  FilledButton(
                    onPressed: _confirm,
                    child: const Text('Simpan'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ActionButton extends StatelessWidget {
  final String label;
  final IconData icon;
  final Color color;
  final bool selected;
  final VoidCallback onTap;

  const _ActionButton({
    required this.label,
    required this.icon,
    required this.color,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            color: selected ? color.withOpacity(0.12) : Colors.transparent,
            borderRadius: BorderRadius.circular(10),
            border: Border.all(
              color: selected ? color : Colors.grey.shade300,
              width: selected ? 2 : 1,
            ),
          ),
          child: Column(
            children: [
              Icon(icon, color: selected ? color : Colors.grey, size: 22),
              const SizedBox(height: 4),
              Text(
                label,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight:
                      selected ? FontWeight.w600 : FontWeight.normal,
                  color: selected ? color : Colors.grey,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
