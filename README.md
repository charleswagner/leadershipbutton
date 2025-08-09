# Leadership Button

AI-powered leadership coach with voice input/output.

## Install (from source)

```bash
python -m pip install --upgrade build
python -m build
pip install dist/leadershipbutton-*.whl
```

## CLI

```bash
leadershipbutton
```

## Google Cloud credentials

We DO NOT ship credentials in the package. Create a service account with access to Text-to-Speech and Speech-to-Text, download its JSON key, and set:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/key.json
export GOOGLE_CLOUD_PROJECT=your-project-id
```

You can also put these in a `.env` file at the project root; the app loads it automatically in development.

## Configuration

Edit `config/api_config.json` (and `config/api_config.development.json` for dev overrides). Notable fields:

- `text_to_speech.language_code` (e.g., `en-US`)
- `text_to_speech.voice_name` (e.g., `en-US-Neural2-H`)
- `audio_settings` sample rates/channels

## Packaging notes

- Packaging is via `pyproject.toml` (setuptools). Runtime data included: `config/*.json`, CSV metadata, and prompt specs.
- Audio libraries or private keys are not packaged.

## Optional helpers

- `scripts/generate_voice_samples.py` – builds short samples for each voice (requires credentials)
- `scripts/play_files_from_stdin.py` – play a list of files from stdin

## Bundle and deploy to Raspberry Pi

Prerequisites on the Pi (the deploy script installs these automatically if possible):

- Debian/Raspberry Pi OS with systemd and apt
- Network access over SSH (e.g., `cwagner@pi.local`)

Steps (from your Mac on the project root):

```bash
# Build the package
python3 -m pip install --upgrade build
python3 -m build

# Deploy (will scp the wheel, set up venv, install deps, and create a systemd service)
bash scripts/deploy_to_pi.sh --host cwagner@pi.local --env .env
```

Optional flags:

- `--dest /home/pi/leadershipbutton` – change install directory
- `--key-file /absolute/path/key.json` – also copy a Google key to the Pi and set GOOGLE_APPLICATION_CREDENTIALS
- `--no-sudo` – if your user has the needed permissions

What the script does:

- Builds the wheel `dist/leadershipbutton-*.whl`
- Copies `.whl` and `.env` (if present) to the Pi
- Installs system dependencies (PortAudio, ffmpeg, build tools)
- Creates venv at `<dest>/.venv` and installs the wheel
- Creates and enables systemd service `leadershipbutton.service` to run at boot
- Starts the service immediately

Start/stop/status on the Pi:

```bash
ssh cwagner@pi.local 'sudo systemctl start leadershipbutton.service'
ssh cwagner@pi.local 'sudo systemctl stop leadershipbutton.service'
ssh cwagner@pi.local 'systemctl status leadershipbutton.service --no-pager'
```

Tail logs:

```bash
ssh cwagner@pi.local 'journalctl -u leadershipbutton.service -f'
```

Troubleshooting:

- apt/dpkg lock: another package manager is running on the Pi. The deploy script now waits, but if you see a lock error:
  ```bash
  ssh cwagner@pi.local
  sudo dpkg --configure -a
  sudo apt-get -o Dpkg::Lock::Timeout=600 -y -f install
  sudo apt-get -o Dpkg::Lock::Timeout=600 update -y
  ```
- Credentials: ensure `.env` on the Pi contains `GOOGLE_APPLICATION_CREDENTIALS` and `GOOGLE_CLOUD_PROJECT`, or deploy with `--key-file`.
