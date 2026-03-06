import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:webview_windows/webview_windows.dart';
import '../../providers/providers.dart';

class AbsensiScreen extends ConsumerStatefulWidget {
  const AbsensiScreen({super.key});

  @override
  ConsumerState<AbsensiScreen> createState() => _AbsensiScreenState();
}

class _AbsensiScreenState extends ConsumerState<AbsensiScreen> {
  final _controller = WebviewController();
  final _urlCtrl = TextEditingController();
  bool _ready = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _initWebView();
  }

  Future<void> _initWebView() async {
    try {
      await _controller.initialize();

      _controller.url.listen((url) {
        if (mounted && url.isNotEmpty) {
          _urlCtrl.text = url;
        }
      });

      final config = ref.read(configProvider).valueOrNull;
      final baseUrl = config?.frontendUrl ?? 'http://localhost:4923';
      final url = '$baseUrl/beranda';
      _urlCtrl.text = url;

      await _controller.loadUrl(url);

      if (mounted) setState(() => _ready = true);
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
        });
      }
    }
  }

  void _navigate() {
    final url = _urlCtrl.text.trim();
    if (url.isNotEmpty) {
      _controller.loadUrl(url);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    _urlCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colors = theme.colorScheme;

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.error_outline, size: 48, color: colors.error),
            const SizedBox(height: 12),
            Text('WebView failed to load',
                style: theme.textTheme.titleMedium),
            const SizedBox(height: 4),
            Text(_error!,
                style:
                    theme.textTheme.bodySmall?.copyWith(color: colors.outline)),
            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: () {
                setState(() => _error = null);
                _initWebView();
              },
              icon: const Icon(Icons.refresh, size: 18),
              label: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (!_ready) {
      return const Center(child: CircularProgressIndicator());
    }

    return Column(
      children: [
        // URL bar
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            color: colors.surface,
            border: Border(
              bottom: BorderSide(color: colors.outlineVariant, width: 1),
            ),
          ),
          child: Row(
            children: [
              IconButton(
                icon: const Icon(Icons.arrow_back, size: 18),
                onPressed: () => _controller.goBack(),
                tooltip: 'Back',
                visualDensity: VisualDensity.compact,
              ),
              IconButton(
                icon: const Icon(Icons.arrow_forward, size: 18),
                onPressed: () => _controller.goForward(),
                tooltip: 'Forward',
                visualDensity: VisualDensity.compact,
              ),
              IconButton(
                icon: const Icon(Icons.refresh, size: 18),
                onPressed: () => _controller.reload(),
                tooltip: 'Reload',
                visualDensity: VisualDensity.compact,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: TextField(
                  controller: _urlCtrl,
                  onSubmitted: (_) => _navigate(),
                  style: const TextStyle(fontSize: 13),
                  decoration: InputDecoration(
                    isDense: true,
                    contentPadding: const EdgeInsets.symmetric(
                        horizontal: 12, vertical: 8),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                      borderSide: BorderSide(color: colors.outlineVariant),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                      borderSide: BorderSide(color: colors.outlineVariant),
                    ),
                    filled: true,
                    fillColor: colors.surfaceContainerLow,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              IconButton(
                icon: const Icon(Icons.home, size: 18),
                onPressed: () {
                  final config = ref.read(configProvider).valueOrNull;
                  final baseUrl =
                      config?.frontendUrl ?? 'http://localhost:4923';
                  _controller.loadUrl('$baseUrl/beranda');
                },
                tooltip: 'Beranda',
                visualDensity: VisualDensity.compact,
              ),
            ],
          ),
        ),
        // WebView
        Expanded(child: Webview(_controller)),
      ],
    );
  }
}
