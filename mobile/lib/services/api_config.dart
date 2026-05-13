import 'package:flutter/foundation.dart';

String get apiBaseUrl {
  const overrideUrl = String.fromEnvironment('SMAT_API_URL', defaultValue: '');
  if (overrideUrl.isNotEmpty) {
    return overrideUrl;
  }

  if (kIsWeb) {
    return 'http://127.0.0.1:8000';
  }

  switch (defaultTargetPlatform) {
    case TargetPlatform.android:
      return 'http://10.0.2.2:8000';
    case TargetPlatform.iOS:
      return 'http://127.0.0.1:8000';
    case TargetPlatform.linux:
    case TargetPlatform.macOS:
    case TargetPlatform.windows:
    case TargetPlatform.fuchsia:
      return 'http://127.0.0.1:8000';
  }
}
