# Android Studio Quick Start

**5-Minute Setup Checklist**

## Prerequisites
- [ ] JDK 17+ installed (`java -version`)
- [ ] 4GB+ RAM available
- [ ] 750MB+ free disk space

## Setup Steps

### 1. Download & Install Android Studio
- [ ] Go to [developer.android.com/studio](https://developer.android.com/studio)
- [ ] Download for your OS (Windows/macOS/Linux)
- [ ] Run installer and select **Custom** to pick SDK location
- [ ] Let installer download SDK components (~500MB)

### 2. Import Project
- [ ] Open Android Studio
- [ ] **File → Open** → select `REPLITCLONE` folder
- [ ] Wait for Gradle indexing (watch status bar)

### 3. Configure SDK (if needed)
- [ ] **File → Project Structure → SDK Location**
- [ ] Verify **Android SDK Location** is set (auto-detected usually)
- [ ] Click **OK**

### 4. Sync Gradle
- [ ] Watch for sync banner at top of editor
- [ ] Click **Sync Now** or wait for auto-sync
- [ ] Ensure no red error messages

### 5. Create Emulator
- [ ] **Tools → Device Manager**
- [ ] Click **Create Device**
- [ ] Select **Pixel 6a** (or similar)
- [ ] Select API Level **35**
- [ ] Click **Finish**
- [ ] Click ▶️ to launch emulator (wait 30-60 seconds)

### 6. Run App
- [ ] Select emulator from dropdown (top toolbar)
- [ ] Click ▶️ **Run** button
- [ ] Wait for build (1-2 mins first time)
- [ ] App appears on emulator

## Result
You should see the Replit Clone app with:
- File explorer panel (left side on tablets)
- Code editor with Python example code
- **Run** button in header
- Console output pane below editor

## Common Issues

**"SDK not found"**
→ File → Project Structure → Configure Android SDK

**Gradle sync hangs**
→ File → Invalidate Caches → Invalidate and Restart

**Emulator won't start**
→ Tools → Device Manager → right-click device → Wipe Data

**App crashes**
→ Build → Clean Project, then Build → Rebuild Project

## Next Steps
- Modify code in `MainActivity.kt`
- Hot-reload: Cmd+Shift+R (macOS) or Ctrl+Shift+R (Windows/Linux)
- Test on physical device (Tools → Device Manager → Connect via USB)

## Need Help?
See **README.md** for detailed troubleshooting and command-line build options.
