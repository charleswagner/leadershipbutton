#!/usr/bin/env python3
import sys
import os
import argparse
import subprocess
from pathlib import Path
from typing import List

AUDIO_EXTS = {".mp3", ".m4a", ".aac", ".wav", ".flac", ".ogg"}


def parse_paths_from_stdin() -> List[Path]:
    items: List[Path] = []
    for raw in sys.stdin.read().splitlines():
        line = raw.strip()
        if not line:
            continue
        # Trim grep-style suffix ":<lineno>" if file doesn't exist as-is
        candidate = line
        if ":" in line and not os.path.exists(line):
            candidate = line.split(":", 1)[0]
        p = Path(candidate).expanduser()
        if p.exists():
            items.append(p)
    return items


def which(cmd: str) -> bool:
    from shutil import which as _which

    return _which(cmd) is not None


def choose_player(prefer: str, files: List[Path]) -> str:
    if prefer and prefer != "auto":
        return prefer
    # prefer ffplay if ogg present
    if any(p.suffix.lower() == ".ogg" for p in files) and which("ffplay"):
        return "ffplay"
    if which("afplay"):
        return "afplay"
    if which("ffplay"):
        return "ffplay"
    return ""


def play(path: Path, player: str, volume: float) -> int:
    if player == "afplay":
        vol = max(0.0, min(1.0, volume))
        cmd = ["afplay", "-v", str(vol), str(path)]
    elif player == "ffplay":
        # Map 0..1 to dB (0.5≈-6dB)
        import math

        db = (
            -30.0
            if volume <= 0
            else min(0.0, max(-30.0, 20.0 * math.log10(max(1e-3, volume))))
        )
        cmd = [
            "ffplay",
            "-nodisp",
            "-autoexit",
            "-hide_banner",
            "-loglevel",
            "error",
            "-af",
            f"volume={db}dB",
            str(path),
        ]
    else:
        print("❌ No audio player found (need afplay or ffplay)", file=sys.stderr)
        return 127
    try:
        return subprocess.run(cmd).returncode
    except KeyboardInterrupt:
        return 130


def main():
    parser = argparse.ArgumentParser(
        description="Play audio files from stdin (pipe ls/grep into this)."
    )
    parser.add_argument(
        "--player",
        default="auto",
        choices=["auto", "afplay", "ffplay"],
        help="Player to use (default auto)",
    )
    parser.add_argument(
        "--volume",
        type=float,
        default=1.0,
        help="Volume (0.0-1.0 for afplay; mapped for ffplay)",
    )
    parser.add_argument(
        "--delay", type=float, default=0.0, help="Seconds to sleep between files"
    )
    parser.add_argument(
        "--list-only", action="store_true", help="List files without playing"
    )
    args = parser.parse_args()

    files = [p for p in parse_paths_from_stdin() if p.suffix.lower() in AUDIO_EXTS]
    if not files:
        print("No playable audio files found on stdin.")
        sys.exit(0)

    player = choose_player(args.player, files)
    if not player:
        print("❌ Neither afplay nor ffplay found in PATH.", file=sys.stderr)
        sys.exit(127)

    print(f"Using player: {player} | {len(files)} file(s)")
    if args.list_only:
        for p in files:
            print(p)
        sys.exit(0)

    import time

    for i, f in enumerate(files, 1):
        print(f"[{i}/{len(files)}] {f}")
        rc = play(f, player, args.volume)
        if rc not in (0, 130):
            print(f"⚠️  Player exit code {rc} for {f}")
        if args.delay > 0:
            time.sleep(args.delay)


if __name__ == "__main__":
    main()
