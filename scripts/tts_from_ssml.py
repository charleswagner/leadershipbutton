#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

# Ensure src is importable when running from repo root
THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[1]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))


from leadership_button.api_client import APIManager, APIConfig

import leadership_button.api_client

print("--- PATH TO THE API CLIENT BEING USED ---")
print(leadership_button.api_client.__file__)
print("-----------------------------------------")


def main():
    parser = argparse.ArgumentParser(
        description="Synthesize SSML to audio using Google TTS via project APIManager."
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        default="-",
        help="Path to SSML file, or - for stdin (default)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="out.wav",
        help="Output audio file path (default: out.wav)",
    )
    args = parser.parse_args()

    # Read SSML
    if args.input == "-" or args.input == "/dev/stdin":
        ssml = sys.stdin.read()
    else:
        ssml = Path(args.input).read_text(encoding="utf-8")

    cfg = APIConfig()
    mgr = APIManager(cfg)

    audio = mgr.text_to_speech_ssml(ssml)
    if not audio:
        print("TTS failed", file=sys.stderr)
        sys.exit(1)

    out_path = Path(args.output)

    # If AudioData-like, prefer its saver
    if hasattr(audio, "save_to_file"):
        ok = audio.save_to_file(str(out_path))
        if not ok:
            # fallback: attempt to write raw bytes
            data = getattr(audio, "data", None)
            if isinstance(data, (bytes, bytearray)):
                out_path.write_bytes(data)
            else:
                print("Could not save audio: unknown format", file=sys.stderr)
                sys.exit(2)
    elif isinstance(audio, (bytes, bytearray)):
        out_path.write_bytes(audio)
    else:
        print("Unexpected audio type returned; not bytes-like", file=sys.stderr)
        sys.exit(2)

    print(f"✅ Saved audio to {out_path.resolve()}")


if __name__ == "__main__":
    main()
