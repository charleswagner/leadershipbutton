#!/usr/bin/env python3
import argparse
import os
import re
from pathlib import Path
from typing import Optional

try:
    from google.cloud import texttospeech
except ImportError as exc:
    raise SystemExit(
        "google-cloud-texttospeech not installed. Install with: pip install google-cloud-texttospeech"
    ) from exc

# Load environment from .env if present
try:
    from dotenv import load_dotenv

    load_dotenv()  # loads .env from current working directory
except Exception:
    pass


def sanitize_filename(text: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9._-]+", "_", text)
    safe = re.sub(r"_+", "_", safe).strip("_")
    return safe or "voice"


def build_audio_config(
    encoding: str, sample_rate: Optional[int]
) -> texttospeech.AudioConfig:
    enc = encoding.lower()
    if enc == "mp3":
        ae = texttospeech.AudioEncoding.MP3
    elif enc in {"wav", "linear16"}:
        ae = texttospeech.AudioEncoding.LINEAR16
    else:
        raise ValueError("encoding must be mp3 or wav")

    kwargs = {
        "audio_encoding": ae,
        "speaking_rate": 1.0,
        "pitch": 0.0,
        "volume_gain_db": 0.0,
    }
    if sample_rate:
        kwargs["sample_rate_hertz"] = int(sample_rate)
    return texttospeech.AudioConfig(**kwargs)


def main():
    parser = argparse.ArgumentParser(
        description="Generate short sample files for all Google TTS voices: 'I am <voice-name>'."
    )
    parser.add_argument(
        "--out",
        default="tmp/voice_samples",
        help="Output directory (default: tmp/voice_samples)",
    )
    parser.add_argument(
        "--language", default=None, help="Filter by language code (e.g., en-US)"
    )
    parser.add_argument(
        "--gender",
        default=None,
        choices=["MALE", "FEMALE", "NEUTRAL"],
        help="Filter by gender",
    )
    parser.add_argument(
        "--encoding",
        default="mp3",
        choices=["mp3", "wav"],
        help="Output encoding (default: mp3)",
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=24000,
        help="Output sample rate Hz (default: 24000)",
    )
    parser.add_argument(
        "--limit", type=int, default=0, help="Limit number of voices (0 = all)"
    )
    args = parser.parse_args()

    # Validate credentials presence for clearer error if missing
    if not (
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("GOOGLE_CLOUD_PROJECT")
    ):
        print(
            "⚠️  Tip: credentials not found in environment. If you have a .env file, ensure it contains GOOGLE_APPLICATION_CREDENTIALS and GOOGLE_CLOUD_PROJECT."
        )

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    client = texttospeech.TextToSpeechClient()
    request = texttospeech.ListVoicesRequest()
    if args.language:
        request.language_code = args.language
    response = client.list_voices(request=request)

    voices = list(response.voices or [])
    if args.gender:
        voices = [v for v in voices if v.ssml_gender.name == args.gender]

    if args.limit and args.limit > 0:
        voices = voices[: args.limit]

    audio_config = build_audio_config(args.encoding, args.sample_rate)
    synthesized = 0

    for idx, v in enumerate(voices, 1):
        lang = (v.language_codes[0] if v.language_codes else "") or "und"
        name = v.name or f"voice_{idx}"
        gender = v.ssml_gender.name if v.ssml_gender else "UNSPECIFIED"

        text = f"I am {name}"
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Use explicit voice name when available; do not also set gender
        voice_params = texttospeech.VoiceSelectionParams(language_code=lang, name=name)

        audio = client.synthesize_speech(
            input=synthesis_input, voice=voice_params, audio_config=audio_config
        )
        ext = ".mp3" if args.encoding.lower() == "mp3" else ".wav"
        filename = f"{idx:03d}_{sanitize_filename(lang)}_{sanitize_filename(gender)}_{sanitize_filename(name)}{ext}"
        out_path = out_dir / filename
        out_path.write_bytes(audio.audio_content)
        synthesized += 1
        print(f"Saved {out_path}")

    print(f"✅ Generated {synthesized} sample files in {out_dir.resolve()}")


if __name__ == "__main__":
    main()
