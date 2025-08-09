#!/usr/bin/env bash
# Deploy Leadership Button to Raspberry Pi (or any Debian-like Linux host)
# - Builds wheel
# - Copies wheel + optional .env + optional key to remote
# - Installs system deps (PortAudio/ffmpeg) and Python deps on remote
# - Creates venv, installs wheel
# - Installs/starts a systemd service that runs the app at boot
# - Shows how to tail logs (journald)

set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 [--host user@pi.local] [--dest /home/user/leadershipbutton] [--env .env] [--key-file /abs/key.json] [--no-sudo] [--force]

Defaults:
  --host    cwagner@pi.local
  --dest    /home/cwagner/leadershipbutton
  --env     .env (optional; copied if present)

Examples:
  $0 --host cwagner@pi.local --env .env --key-file /Users/me/Downloads/key.json
  $0 --host cwagner@pi.local --no-sudo
  $0 --host cwagner@pi.local --force   # force reinstall of wheel on remote
EOF
}

HOST="cwagner@pi.local"
DEST="/home/cwagner/leadershipbutton"
ENV_FILE=".env"
KEY_FILE=""
NO_SUDO=false
FORCE_REINSTALL=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --host) HOST="$2"; shift 2 ;;
    --dest) DEST="$2"; shift 2 ;;
    --env) ENV_FILE="$2"; shift 2 ;;
    --key-file) KEY_FILE="$2"; shift 2 ;;
    --no-sudo) NO_SUDO=true; shift 1 ;;
    --force) FORCE_REINSTALL=true; shift 1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 1 ;;
  esac
done

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

say(){ echo -e "\033[1;32m$*\033[0m"; }
warn(){ echo -e "\033[1;33m$*\033[0m"; }

# 1) Build wheel
say "Building wheel…"
python3 -m pip install --quiet --upgrade build >/dev/null 2>&1 || true
python3 -m build
WHEEL="$(ls -t dist/leadershipbutton-*.whl | head -n1 || true)"
if [[ -z "$WHEEL" ]]; then
  echo "Failed to build/find wheel in dist/." >&2
  exit 2
fi
say "Wheel: $WHEEL"

# 2) Copy artifacts to remote
say "Creating remote directory and copying artifacts…"
ssh "$HOST" "mkdir -p '$DEST'"
scp "$WHEEL" "$HOST:$DEST/"

# Stage prompt files (do NOT install yet; install on remote after venv is ready)
LOCAL_PROMPTS_DIR="$ROOT/docs/specs/leadership_button"
if [[ -d "$LOCAL_PROMPTS_DIR" ]]; then
  say "Staging prompt markdowns to remote"
  ssh "$HOST" "mkdir -p '$DEST/prompts'"
  scp -r "$LOCAL_PROMPTS_DIR" "$HOST:$DEST/prompts/"
else
  warn "Local prompt directory not found: $LOCAL_PROMPTS_DIR"
fi

REMOTE_ENV="$DEST/.env"
if [[ -f "$ENV_FILE" ]]; then
  say "Copying env file to $REMOTE_ENV"
  scp "$ENV_FILE" "$HOST:$REMOTE_ENV"
else
  warn "Local env file '$ENV_FILE' not found. Ensure remote $REMOTE_ENV contains GOOGLE_* vars."
fi

if [[ -n "$KEY_FILE" ]]; then
  if [[ ! -f "$KEY_FILE" ]]; then
    echo "Key file not found: $KEY_FILE" >&2; exit 2
  fi
  BASENAME="$(basename "$KEY_FILE")"
  REMOTE_KEY="$DEST/$BASENAME"
  say "Copying key file to $REMOTE_KEY"
  scp "$KEY_FILE" "$HOST:$REMOTE_KEY"
  # Ensure env references copied key
  ssh "$HOST" "set -e; touch '$REMOTE_ENV'; grep -q '^GOOGLE_APPLICATION_CREDENTIALS=' '$REMOTE_ENV' || echo GOOGLE_APPLICATION_CREDENTIALS='$REMOTE_KEY' >> '$REMOTE_ENV'"
fi

# 3-6) Remote: install deps, venv, wheel, systemd service
SUDO="sudo"; $NO_SUDO && SUDO=""
SERVICE_NAME="leadershipbutton.service"
WHEEL_BN_LOCAL="$(basename "$WHEEL")"

say "Configuring remote host and installing service…"
ssh "$HOST" DEST="$DEST" REMOTE_ENV="$REMOTE_ENV" WHEEL_BN="$WHEEL_BN_LOCAL" SUDO="$SUDO" SERVICE_NAME="$SERVICE_NAME" FORCE_REINSTALL="$FORCE_REINSTALL" bash -s <<'REMOTE'
set -euo pipefail
DEST_DIR="${DEST}"
WHEEL_BN="${WHEEL_BN}"
ENV_PATH="${REMOTE_ENV}"
SUDO_CMD="${SUDO:-}"
SERVICE_NAME="${SERVICE_NAME:-leadershipbutton.service}"
FORCE_REINSTALL="${FORCE_REINSTALL:-false}"

# Install system deps (Debian/Raspbian)
if command -v apt-get >/dev/null 2>&1; then
  echo "[remote] Installing system dependencies…"
  export DEBIAN_FRONTEND=noninteractive
  if command -v fuser >/dev/null 2>&1; then
    while ${SUDO_CMD:-} fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1; do echo "[remote] Waiting for dpkg lock to be released…"; sleep 3; done
  else
    while pgrep -f 'apt|dpkg' >/dev/null 2>&1; do echo "[remote] Waiting for apt/dpkg to finish…"; sleep 3; done
  fi
  ${SUDO_CMD:-} apt-get -o Dpkg::Lock::Timeout=300 update -y
  ${SUDO_CMD:-} apt-get -o Dpkg::Lock::Timeout=300 install -y \
      python3-venv python3-dev build-essential \
      portaudio19-dev libasound2-dev libportaudio2 libportaudiocpp0 ffmpeg
fi

mkdir -p "$DEST_DIR"
cd "$DEST_DIR"

# Stop existing service and processes
if systemctl list-unit-files | grep -q "$SERVICE_NAME"; then
  ${SUDO_CMD:-} systemctl stop "$SERVICE_NAME" || true
  ${SUDO_CMD:-} systemctl disable "$SERVICE_NAME" || true
fi
pkill -f "python .* -m leadership_button\.runner" || true
pkill -f "leadership_button\.runner" || true

# Python venv + install wheel
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install pyaudio tenacity
if [ "$FORCE_REINSTALL" = "true" ]; then
  python3 -m pip install --upgrade --force-reinstall "${WHEEL_BN}"
else
  python3 -m pip install --upgrade "${WHEEL_BN}"
fi

# Install prompt markdowns into the venv lib docs path expected by the app
if [ -d "$DEST_DIR/prompts/leadership_button" ]; then
  PYVER=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
  DST="$DEST_DIR/.venv/lib/python${PYVER}/docs/specs/leadership_button"
  mkdir -p "$DST"
  cp -f "$DEST_DIR/prompts/leadership_button"/*.md "$DST"/ || true
  echo "[remote] Installed prompt files to $DST"
fi

# Create logs dir and set env for file logging
mkdir -p "$DEST_DIR/logs"

# Create systemd unit (do not overwrite user configs/env beyond EnvironmentFile)
REMOTE_USER=$(whoami)
cat > /tmp/${SERVICE_NAME} <<EOF
[Unit]
Description=Leadership Button
After=network.target sound.target

[Service]
Type=simple
User=${REMOTE_USER}
WorkingDirectory=$DEST_DIR
EnvironmentFile=$ENV_PATH
Environment=PYTHONUNBUFFERED=1
Environment=LB_LOG_DIR=$DEST_DIR/logs
# Access to input devices for evdev
SupplementaryGroups=input
ExecStart=$DEST_DIR/.venv/bin/python -m leadership_button.runner
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

${SUDO_CMD:-} mv /tmp/${SERVICE_NAME} /etc/systemd/system/${SERVICE_NAME}
${SUDO_CMD:-} systemctl daemon-reload
${SUDO_CMD:-} systemctl enable ${SERVICE_NAME}
${SUDO_CMD:-} systemctl restart ${SERVICE_NAME}

# Show status and last logs
${SUDO_CMD:-} systemctl status ${SERVICE_NAME} --no-pager || true
journalctl -u ${SERVICE_NAME} -n 50 --no-pager || true
REMOTE

say "Deployment complete. To follow logs, run:"
echo "  ssh $HOST 'journalctl -u $SERVICE_NAME -f'"
echo "  ssh $HOST 'tail -f $DEST/logs/leadershipbutton.log'"
