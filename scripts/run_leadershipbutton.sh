#!/usr/bin/env bash
# Cross-platform launcher for Leadership Button
# - Creates .venv
# - Installs system deps (PortAudio, ffmpeg) on macOS/Linux (Raspberry Pi)
# - Installs Python deps incl. PyAudio + tenacity
# - Loads credentials from args or .env
# - Installs wheel or source, then starts the app

set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 [--key /abs/path/key.json] [--project-id PROJECT] [--mode wheel|source] [--wheel /abs/path.whl] [--no-sudo]

Examples:
  $0 --key /path/key.json --project-id my-gcp-project
  $0 --mode source
  $0 --wheel dist/leadershipbutton-0.1.0-py3-none-any.whl

Note: On Raspberry Pi (Debian/Ubuntu), this will run 'sudo apt-get' to install system libs unless --no-sudo is used.
EOF
}

# Defaults
MODE="wheel"
WHEEL_PATH=""
NO_SUDO=false

KEY="${GOOGLE_APPLICATION_CREDENTIALS:-}"
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --key) KEY="$2"; shift 2 ;;
    --project-id) PROJECT_ID="$2"; shift 2 ;;
    --mode) MODE="$2"; shift 2 ;;
    --wheel) WHEEL_PATH="$2"; shift 2 ;;
    --no-sudo) NO_SUDO=true; shift 1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 1 ;;
  esac
done

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Load .env if present
if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi
# CLI overrides
[[ -n "$KEY" ]] && export GOOGLE_APPLICATION_CREDENTIALS="$KEY"
[[ -n "$PROJECT_ID" ]] && export GOOGLE_CLOUD_PROJECT="$PROJECT_ID"

if [[ -z "${GOOGLE_APPLICATION_CREDENTIALS:-}" || -z "${GOOGLE_CLOUD_PROJECT:-}" ]]; then
  echo "ERROR: GOOGLE_APPLICATION_CREDENTIALS and GOOGLE_CLOUD_PROJECT must be set (via .env or args)." >&2
  exit 2
fi
if [[ ! -f "${GOOGLE_APPLICATION_CREDENTIALS}" ]]; then
  echo "ERROR: Key file not found: ${GOOGLE_APPLICATION_CREDENTIALS}" >&2
  exit 2
fi

say() { echo -e "\033[1;32m$*\033[0m"; }
warn() { echo -e "\033[1;33m$*\033[0m"; }
info() { echo "[*] $*"; }

install_system_deps_macos() {
  if ! command -v brew >/dev/null 2>&1; then
    warn "Homebrew not found. Install from https://brew.sh and re-run, or install PortAudio + ffmpeg manually."
    return
  fi
  say "Installing macOS system deps via Homebrew (portaudio, ffmpeg)…"
  brew list portaudio >/dev/null 2>&1 || brew install portaudio
  brew list ffmpeg >/dev/null 2>&1 || brew install ffmpeg
}

install_system_deps_debian() {
  local SUDO="sudo"
  $NO_SUDO && SUDO=""
  if ! command -v apt-get >/dev/null 2>&1; then
    warn "apt-get not found. Skipping system deps; ensure PortAudio and ffmpeg are installed."
    return
  fi
  say "Installing Debian/Raspberry Pi system deps (portaudio, ffmpeg, build tools)…"
  $SUDO apt-get update -y
  $SUDO apt-get install -y \
    python3-venv python3-dev build-essential \
    portaudio19-dev libasound2-dev libportaudio2 libportaudiocpp0 \
    ffmpeg
}

install_system_deps() {
  UNAME_S="$(uname -s || true)"
  if [[ "$UNAME_S" == "Darwin" ]]; then
    install_system_deps_macos
  else
    # Assume Debian/Ubuntu/Raspberry Pi by default
    install_system_deps_debian
  fi
}

create_venv() {
  if [[ ! -d .venv ]]; then
    say "Creating virtual environment .venv"
    python3 -m venv .venv
  fi
  # shellcheck disable=SC1091
  source .venv/bin/activate
  python3 -m pip install --upgrade pip
}

install_python_deps() {
  say "Installing Python runtime deps (PyAudio, tenacity)…"
  # PyAudio needs PortAudio headers present (system deps installed above)
  python3 -m pip install --upgrade \
    pyaudio tenacity
}

install_app() {
  if [[ "$MODE" == "wheel" ]]; then
    if [[ -z "$WHEEL_PATH" ]]; then
      WHEEL_PATH="$(ls -t dist/leadershipbutton-*.whl 2>/dev/null | head -n1 || true)"
      if [[ -z "$WHEEL_PATH" ]]; then
        warn "No wheel found in ./dist. Building one now…"
        python3 -m pip install --upgrade build
        python3 -m build
        WHEEL_PATH="$(ls -t dist/leadershipbutton-*.whl 2>/dev/null | head -n1 || true)"
      fi
    fi
    say "Installing app wheel: $WHEEL_PATH"
    python3 -m pip install "$WHEEL_PATH"
  elif [[ "$MODE" == "source" ]]; then
    say "Installing app in editable mode from source"
    python3 -m pip install -e .
  else
    echo "Unknown --mode '$MODE' (use 'wheel' or 'source')." >&2
    exit 3
  fi
}

print_env() {
  echo "Credentials:"
  echo "  GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}"
  echo "  GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}"
}

run_app() {
  if command -v leadershipbutton >/dev/null 2>&1; then
    say "Starting leadershipbutton…"
    exec leadershipbutton
  else
    say "Starting via module runner…"
    exec python3 -m leadership_button.runner
  fi
}

# --- Main flow ---
install_system_deps
create_venv
install_python_deps
install_app
print_env

# Optional helper: detect system player availability for helper scripts
if command -v afplay >/dev/null 2>&1; then
  info "afplay detected"
elif command -v ffplay >/dev/null 2>&1; then
  info "ffplay detected"
else
  info "No afplay/ffplay detected. Core app playback uses PyAudio; helper scripts may need a player."
fi

run_app
