# Replit Clone (Android)

This repository now contains a native Android prototype of a Replit-style mobile IDE built with Kotlin + Jetpack Compose.

## Features

- Workspace/file explorer panel (tablet and large screens)
- File tabs for quick switching
- New file action from the workspace header
- File explorer filtering/search
- Rich editor area with line numbers and animated status header
- Run button with simulated execution pipeline and console output
- Styled terminal output card with runtime info
- Galaxy S24 Ultra optimized compact layout tuning (portrait)
- Minimalistic black + neon-blue visual theme
- Responsive layout:
	- Compact mode for phones
	- Multi-pane mode for tablets/foldables

## Datasets

The repo includes starter CSV datasets in `datasets/raw`:

- `iris.csv`
- `penguins.csv`
- `titanic.csv`

Refresh or re-download at any time:

```bash
./scripts/download-datasets.sh
```

Optional output folder:

```bash
./scripts/download-datasets.sh ./datasets/raw
```

## Tech Stack

- Kotlin
- Jetpack Compose (Material 3)
- Android Gradle Plugin

## Project Structure

- `app/src/main/java/com/replitclone/app/MainActivity.kt`: UI and local editor state
- `app/src/main/java/com/replitclone/app/ui/theme/*`: Compose theme setup
- `app/src/main/res/*`: Android resources and manifest dependencies

## Generate Android SDK

If your machine does not already have Android SDK tools configured, run:

```bash
./scripts/generate-android-sdk.sh
```

Optional custom SDK location:

```bash
./scripts/generate-android-sdk.sh "$HOME/.android/sdk"
```

This installs command-line tools, platform tools, API 35 platform, build-tools 35.0.0, and writes `local.properties`.

## Android Studio Setup

### Prerequisites

- **JDK 17** or later (check with `java -version`)
- **macOS, Windows, or Linux** (4GB RAM minimum, 8GB+ recommended)
- **250 MB+ disk space** for Android Studio
- **500 MB+ additional space** for Android SDK components

### Step 1: Install Android Studio

1. Download Android Studio from [developer.android.com/studio](https://developer.android.com/studio)
2. Install following your OS instructions:
   - **macOS**: Drag `.app` to Applications folder
   - **Windows**: Run installer .exe or use Windows Subsystem for Android
   - **Linux**: Extract tarball and run `studio.sh` from `bin/` folder

3. Launch Android Studio and complete initial setup wizard:
   - Accept license agreements
   - Choose install location for SDK (default: `$HOME/Library/Android/sdk` on macOS, `%APPDATA%\Android\sdk` on Windows)
   - Wait for component downloads

### Step 2: Import This Project

1. **Start Android Studio** and click **"Open"** (or File → Open)
2. Navigate to the `REPLITCLONE` folder root and click **OK**
3. Wait for Gradle indexing to complete (watch the bottom status bar)
4. If prompted: **Trust Project**

### Step 3: Configure SDK in Android Studio

After opening:

1. **File → Project Structure**
2. Under **SDK Location**, ensure:
   - **Android SDK Location** points to your SDK installation
   - If not set, click **"Edit"** and select/create SDK directory
   - Android Studio will auto-download missing components

Alternatively, if generating SDK manually:

```bash
./scripts/generate-android-sdk.sh
```

Then in Android Studio, File → Project Structure → SDK Location → set both:
- Android SDK
- JDK (should auto-detect Java 17+)

### Step 4: Sync Gradle

After project opens:

1. Click **File → Sync Now** (or look for banner at top suggesting sync)
2. Wait for Gradle sync to complete—this downloads dependencies
3. Watch status bar; when done, you should see no red errors

If sync fails with SDK errors:
- Verify SDK is configured (Step 3)
- Clean cache: **File → Invalidate Caches → Invalidate and Restart**

### Step 5: Set Up Android Emulator (or Connect Device)

#### Option A: Create Android Emulator

1. Click **Tools → Device Manager** (or AVD Manager icon in toolbar)
2. Click **"Create Device"**
3. Select device profile (e.g., **Pixel 6a**) → **Next**
4. Select API Level (**35** recommended) → **Next**
5. Name it (e.g., "Pixel6a35") → **Finish**
6. Device list shows your emulator; click the ▶️ **Play** icon to launch

Launching emulator may take 30–60 seconds. Wait for home screen.

#### Option B: Use Physical Device

1. Connect Android phone via USB cable
2. Enable **Developer Mode**:
   - Settings → About Phone → tap Build Number 7 times
   - Settings → System → Developer Options → enable USB Debugging
3. Accept USB authorization prompt on phone
4. Emulator dropdown in Android Studio should show your device

### Step 6: Build and Run the App

1. In Android Studio, select emulator/device from dropdown (top toolbar)
2. Click **▶️ Run** button (or Shift+F10)
3. First build takes 1–2 minutes; subsequent builds are faster
4. App launches automatically once build completes

#### What to See

- Editor pane with monospace code (Python example code)
- File explorer on left/tablet, file tabs above editor
- **Run** button in top header
- Click **Run** → console output panel shows simulated build pipeline

### Troubleshooting

| Issue | Solution |
|-------|----------|
| "SDK not found" | File → Project Structure → Configure SDK location |
| Gradle sync stuck | File → Invalidate Caches → Invalidate and Restart |
| Emulator won't start | Tools → Device Manager → right-click device → Wipe Data, then launch |
| App crashes on launch | Rebuild: Build → Clean Project, then Build → Rebuild Project |
| "Waiting for debugger" | Click ⏸️ Pause or wait 30s; if hangs, reconnect device/emulator |
| Gradle/Kotlin daemon crash on release | `./gradlew --stop && ./gradlew --no-daemon :app:assembleRelease -x lint` |

### Build from Terminal

If you prefer command-line builds (after SDK setup):

```bash
# Debug APK
./gradlew assembleDebug

# Release APK
./gradlew assembleRelease

# Release AAB
./gradlew bundleRelease

# Install and run on emulator
./gradlew installDebug

# Full build + run via gradle (requires emulator running)
./gradlew connectedAndroidTest
```

Output APK: `app/build/outputs/apk/debug/app-debug.apk`

### Run Configurations

To customize run behavior in Android Studio:

1. **Run → Edit Configurations**
2. Select "app" → adjust Emulator/Device, execution, and logging
3. Click **OK** and use **▶️ Run** or **🐛 Debug** buttons

### Next Steps

- **Edit code**: Modify `MainActivity.kt` and hot-reload (Cmd+Shift+R on macOS, Ctrl+Shift+R on Windows/Linux)
- **Add features**: Create new Compose functions or add libraries in `app/build.gradle.kts`
- **Test on device**: Use physical phone for real performance and UI feel
- **Build release**: Build → Build Bundle(s) / APK(s) → Build APK(s)