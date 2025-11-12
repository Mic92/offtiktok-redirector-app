# TikTok Redirect App

This Android app intercepts TikTok links and redirects them to OffTikTok (offtiktok.com) in a WebView.

Status: Under development

## Features

- Registers as a handler for TikTok links (tiktok.com, vm.tiktok.com, vt.tiktok.com)
- Automatically replaces `tiktok.com` with `offtiktok.com`, opens it in an in-app WebView
- Available through F-Droid

## 🚀 Quick Install

Download the latest APK from [GitHub Releases](https://github.com/Mic92/offtiktok-redirector-app/releases/latest)

## 📦 For Developers

### Prerequisites

- Android Studio (Arctic Fox or newer)
- Android SDK (API level 24 or higher)
- JDK 17 or higher
- Git

### Initial Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Mic92/offtiktok-redirector-app.git
   cd offtiktok-redirector-app
   ```

2. **Open in Android Studio:**
   - Launch Android Studio
   - Select "Open an Existing Project"
   - Navigate to the `offtiktok-redirector-app` folder
   - Click "OK"

3. **Sync Gradle:**
   - Android Studio should automatically sync Gradle
   - If not, click "File" → "Sync Project with Gradle Files"

### Building Locally

#### Debug Build

```bash
./gradlew assembleDebug
```

APK location: `app/build/outputs/apk/debug/app-debug.apk`

#### Release Build (Unsigned)

```bash
./gradlew assembleRelease
```

## 🔧 How It Works

The app uses Android's Intent Filter system to register for TikTok URLs:

1. **Intent filters** register for tiktok.com domains
2. When a TikTok link is clicked, Android shows chooser with your app
3. App **parses the URL** and replaces domain with `offtiktok.com`
4. **Preserves all** query parameters and URL fragments
5. **Redirects to browser** - opens in your default browser (Firefox, Chrome, etc.)
6. App **immediately closes** - no background processes

## 📄 License

Apache-2.0
