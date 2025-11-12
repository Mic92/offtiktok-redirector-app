# TikTok Redirect App

This Android app intercepts TikTok links and redirects them to OffTikTok (offtiktok.com) in a WebView.

## Features

- Registers as a handler for TikTok links (tiktok.com, vm.tiktok.com, vt.tiktok.com)
- Automatically replaces `tiktok.com` with `offtiktok.com`, opens it in an in-app WebView
- Available through F-Droid

## 🚀 Quick Install

### Option 1: F-Droid Repository (Recommended)

Add this repository to your F-Droid client:

```
https://Mic92.github.io/TikTokRedirect/fdroid/repo
```

**New releases are published automatically on every push to main!**

### Option 2: Direct APK Download

Download the latest APK from [GitHub Releases](https://github.com/Mic92/TikTokRedirect/releases/latest)

## 📦 For Developers

### Prerequisites

- Android Studio (Arctic Fox or newer)
- Android SDK (API level 24 or higher)
- JDK 17 or higher
- Git

### Initial Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Mic92/TikTokRedirect.git
   cd TikTokRedirect
   ```

2. **Open in Android Studio:**
   - Launch Android Studio
   - Select "Open an Existing Project"
   - Navigate to the `TikTokRedirect` folder
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

### Setting Up CI/CD

#### 1. Generate Signing Keystore

Run the setup script:

```bash
chmod +x scripts/setup_signing.sh
./scripts/setup_signing.sh
```

This will:

- Generate a keystore file
- Provide the base64-encoded keystore
- Show you the GitHub secrets you need to add

#### 2. Add GitHub Secrets

Go to your repository settings: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these secrets:

- `KEYSTORE_BASE64` - Base64-encoded keystore (from setup script)
- `KEY_ALIAS` - Key alias (default: `tiktokredirect`)
- `KEYSTORE_PASSWORD` - Password for the keystore
- `KEY_PASSWORD` - Password for the key

#### 3. Set Up GitHub Pages for F-Droid

Initialize the gh-pages branch:

```bash
chmod +x scripts/setup_ghpages.sh
./scripts/setup_ghpages.sh
```

Then:

1. Push the gh-pages branch: `git push -u origin gh-pages`
2. Enable GitHub Pages:
   - Go to **Settings** → **Pages**
   - Source: **Deploy from branch**
   - Branch: **gh-pages** / (root)
3. Wait a few minutes for deployment

#### 4. Update Repository URLs

Replace `YOUR_USERNAME` in these files with your GitHub username:

- `.github/workflows/build.yml`
- `scripts/generate_fdroid_repo.py`
- `scripts/setup_ghpages.sh` (in the generated index.html)

### CI/CD Workflow

The GitHub Actions workflow automatically:

1. **On every push to main:**
   - Auto-generates version from date/time (e.g., `2025.1112.1430`)
   - Updates build.gradle with new version
   - Builds and signs release APK
   - Creates/updates GitHub Release
   - Updates F-Droid repository
   - Deploys to GitHub Pages

2. **On manual version tags (v\*):**
   - Uses your specified version
   - Builds and signs release APK
   - Creates GitHub Release
   - Updates F-Droid repository
   - Deploys to GitHub Pages

3. **On pull requests:**
   - Builds debug APK for testing
   - No deployment

#### Automatic Releases (Recommended)

Just push to main - versions are generated automatically!

```bash
git add .
git commit -m "Add new feature"
git push  # ← Automatically creates a release!
```

**Version Format:**

- Version Name: `YYYY.MMDD.HHMM` (e.g., `2025.1112.1430`)
- Version Code: `YYYYMMDDHHmm` (integer for Android)

#### Manual Releases (Optional)

If you prefer manual version control:

1. Update version in `app/build.gradle`:

   ```gradle
   versionCode 2
   versionName "1.1"
   ```

2. Commit and tag:

   ```bash
   git add app/build.gradle
   git commit -m "Release version 1.1"
   git tag v1.1
   git push && git push --tags
   ```

3. GitHub Actions will use your manual version instead of auto-generated one

### Dependabot Integration

Dependabot automatically keeps your dependencies up to date:

- **Monitors:** Gradle dependencies and GitHub Actions versions
- **Frequency:** Weekly checks on Mondays
- **Groups:** Related dependencies together (androidx, kotlin, google)
- **Creates PRs:** With changelogs and CI testing

**Workflow:**

1. Dependabot creates PR with dependency updates
2. GitHub Actions builds and tests automatically
3. You review and merge the PR
4. Auto-deployment publishes the new version!

See [DEPENDABOT.md](DEPENDABOT.md) for:

- Configuration options
- Auto-merge setup
- Security best practices

## 📱 Usage

1. Install the app (via F-Droid or direct APK)
2. Click on any TikTok link
3. When prompted, choose "TikTok Redirect"
4. Optionally select "Always" to make it the default handler
5. The app will automatically redirect to OffTikTok

## 🔧 How It Works

The app uses Android's Intent Filter system to register for TikTok URLs. When a link is clicked:

1. Android Intent Filter intercepts the TikTok URL
2. App parses the URL using `Uri` class
3. Replaces the domain with `offtiktok.com`
4. Preserves all query parameters and fragments
5. Loads in WebView with JavaScript enabled

## 📋 Permissions

- **INTERNET**: Required for the WebView to load web content

## 🛠️ F-Droid Repository Structure

```
gh-pages/
├── index.html              # User-facing page
├── fdroid/
│   ├── repo/
│   │   ├── *.apk          # APK files
│   │   ├── index.xml      # F-Droid index (legacy)
│   │   └── index-v1.json  # F-Droid index (modern)
│   └── icon.png           # Repository icon
└── .nojekyll              # Prevent Jekyll processing
```

## 🐛 Troubleshooting

### Build Issues

- Ensure you have JDK 17 installed
- Clear gradle cache: `./gradlew clean`
- Invalidate caches in Android Studio

### F-Droid Not Showing Updates

- Check that GitHub Pages is enabled
- Verify the repository URL is correct
- Wait a few minutes after pushing updates
- Try refreshing repositories in F-Droid

### APK Signing Failed in CI

- Verify all GitHub secrets are set correctly
- Check that KEYSTORE_BASE64 is valid base64
- Ensure passwords match your keystore

## 📄 License

Apache-2.0

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⚠️ Notes

- Requires Android 7.0 (API level 24) or higher
- JavaScript is enabled in WebView for full functionality
- Back button navigates through WebView history before closing
- Keep your keystore and passwords secure - they cannot be recovered!
