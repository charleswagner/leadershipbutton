from src.leadership_button.sound_suggester import SoundSuggester


def test_suggest_basic(monkeypatch):
    rows = [
        {
            "filename": "mixkit-gentle-rain-1.mp3",
            "audio_type": "song",
            "kit_title": "Gentle Rain",
            "kit_tags": "rain,ambient,soft",
            "kit_category": "ambient",
            "duration": 30.0,
            "google_cloud_url": "https://storage.googleapis.com/cwsounds/mixkit/gentle-rain.mp3",
        },
        {
            "filename": "mixkit-wing-flap-24.wav",
            "audio_type": "sfx",
            "kit_title": "Wing Flap",
            "kit_tags": "wing,flap,dragon",
            "kit_category": "creature",
            "duration": 1.2,
            "google_cloud_url": "https://storage.googleapis.com/cwsounds/mixkit/wing-flap.wav",
        },
    ]

    suggester = SoundSuggester(csv_path="/dev/null")
    # monkeypatch rows
    suggester.rows = rows

    intent = {
        "request": "story",
        "tone": "gentle",
        "context": "a comforting bedtime story about a friendly dragon in a rainy castle",
        "pieces": [{"name": "Money the Dragon", "description": "friendly"}],
    }
    picks = suggester.suggest(intent, limit=5)
    assert len(picks) >= 1
    # Ensure rain music is preferred
    assert any("rain" in (p.get("display_title", "").lower()) for p in picks)
