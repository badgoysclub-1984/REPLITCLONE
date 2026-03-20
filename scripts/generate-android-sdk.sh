#!/usr/bin/env bash
set -euo pipefail

# Generates a local Android SDK installation and wires this repo to it.
# Usage: ./scripts/generate-android-sdk.sh [sdk_root]

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SDK_ROOT="${1:-$HOME/android-sdk}"
API_LEVEL="${API_LEVEL:-35}"
BUILD_TOOLS="${BUILD_TOOLS:-35.0.0}"
CMDLINE_TOOLS_ZIP_URL="${CMDLINE_TOOLS_ZIP_URL:-https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip}"

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

need_cmd curl
need_cmd unzip

echo "[1/6] Preparing SDK root: $SDK_ROOT"
mkdir -p "$SDK_ROOT/cmdline-tools"

TOOLS_DIR="$SDK_ROOT/cmdline-tools/latest"
SDKMANAGER_BIN="$TOOLS_DIR/bin/sdkmanager"

if [[ ! -x "$SDKMANAGER_BIN" ]]; then
  echo "[2/6] Downloading Android command line tools"
  TMP_DIR="$(mktemp -d)"
  trap 'rm -rf "$TMP_DIR"' EXIT

  ZIP_PATH="$TMP_DIR/cmdline-tools.zip"
  curl -L "$CMDLINE_TOOLS_ZIP_URL" -o "$ZIP_PATH"

  echo "[3/6] Installing command line tools"
  unzip -q "$ZIP_PATH" -d "$TMP_DIR/unpacked"
  rm -rf "$TOOLS_DIR"
  mkdir -p "$TOOLS_DIR"

  if [[ -d "$TMP_DIR/unpacked/cmdline-tools" ]]; then
    cp -R "$TMP_DIR/unpacked/cmdline-tools/." "$TOOLS_DIR/"
  else
    echo "Unexpected archive layout for command line tools." >&2
    exit 1
  fi
fi

echo "[4/6] Installing SDK packages"
export ANDROID_SDK_ROOT="$SDK_ROOT"
export PATH="$TOOLS_DIR/bin:$SDK_ROOT/platform-tools:$PATH"

yes | "$SDKMANAGER_BIN" --sdk_root="$SDK_ROOT" --licenses >/dev/null || true
"$SDKMANAGER_BIN" --sdk_root="$SDK_ROOT" \
  "platform-tools" \
  "platforms;android-$API_LEVEL" \
  "build-tools;$BUILD_TOOLS"

echo "[5/6] Writing local.properties"
printf 'sdk.dir=%s\n' "$SDK_ROOT" > "$REPO_ROOT/local.properties"

echo "[6/6] Done"
echo "SDK root: $SDK_ROOT"
echo "Project local.properties: $REPO_ROOT/local.properties"
