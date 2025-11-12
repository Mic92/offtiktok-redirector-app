# OffTikTok Redirector App

A lightweight Android app that intercepts TikTok links and automatically redirects them to OffTikTok (offtiktok.com) in your default browser.

## Features

- **Intercepts TikTok links** - Registers as handler for all TikTok domains
- **Share menu support** - Appears when sharing TikTok URLs from any app
- **All TikTok domains** - Handles tiktok.com, www.tiktok.com, vm.tiktok.com, vt.tiktok.com
- **Automatic redirect** - Replaces `tiktok.com` with `offtiktok.com` and opens in browser
- **Ultra-lightweight** - Zero external dependencies, ~3MB APK
- **Zero permissions** - No INTERNET, no storage, nothing

## Quick Install

Download the latest APK from [GitHub Releases](https://github.com/Mic92/offtiktok-redirector-app/releases/latest)

## Usage

### Clicking Links

1. Click any TikTok link (in browser, messages, etc.)
2. Android shows a chooser dialog
3. Select "TikTok Redirect"
4. Video opens in OffTikTok in your default browser

### Sharing URLs

1. Find a TikTok link in any app
2. Tap "Share"
3. Select "TikTok Redirect"
4. Opens in OffTikTok in your browser

### Setting as Default

After selecting the app once, choose "Always" to skip the chooser in future.

## How It Works

1. Intent filters register for tiktok.com domains
2. When a TikTok link is clicked or shared, Android offers your app as an option
3. App parses the URL and replaces domain with `offtiktok.com`
4. Preserves all query parameters and URL fragments
5. Redirects to browser - opens in your default browser
6. App immediately closes - no background processes

## For Developers

### Prerequisites

- Nix package manager (recommended)
- OR: JDK 17, Android SDK API 35, Kotlin

### Building with Nix

```bash
# Enter development environment
nix develop

# Build debug APK
./gradlew assembleDebug

# Install on connected device
./gradlew installDebug
```

APK location: `app/build/outputs/apk/debug/app-debug.apk`

### Building without Nix

```bash
# Ensure you have JDK 17 and Android SDK installed
./gradlew assembleDebug
```

### Testing

```bash
# Install on device
adb install app/build/outputs/apk/debug/app-debug.apk

# Test with a TikTok URL
adb shell am start -a android.intent.action.VIEW \
  -d "https://www.tiktok.com/@user/video/123"
```

The app should appear in the Android chooser dialog.

### Development Tools

The project includes formatters and linters via `flake.nix`:

- **nixfmt** - Nix code formatting
- **ktlint** - Kotlin linting and formatting
- **shellcheck** - Shell script linting
- **actionlint** - GitHub Actions workflow linting

Run all formatters: `nix fmt`

## CI/CD

GitHub Actions automatically:

1. **On every push to main:**
   - Generates version from date/time (e.g., `2025.1112.1430`)
   - Builds and signs release APK
   - Creates GitHub Release with downloadable APK

2. **On pull requests:**
   - Builds debug APK for testing
   - No deployment

### Signing Setup

Generate signing keys:

```bash
nix develop
./scripts/setup_signing.sh
```

Then add these 3 GitHub secrets (from script output):

- `KEYSTORE_BASE64` - Base64-encoded keystore
- `KEY_ALIAS` - Key alias (default: `tiktokredirect`)
- `KEYSTORE_PASSWORD` - Password for the keystore and key

## Permissions

None! This app requires zero permissions - it only redirects URLs to your browser.

## Troubleshooting

### App doesn't appear in chooser

- Clear app defaults: Settings → Apps → TikTok Redirect → Open by default → Clear defaults
- Clear browser defaults: Settings → Apps → Firefox/Chrome → Open by default → Clear defaults
- Try clicking the TikTok link again

### Can't install APK

- Enable "Install from Unknown Sources" in Android settings
- Or use: `adb install app-debug.apk`

## License

Apache-2.0
