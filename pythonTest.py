import os
from google.cloud import texttospeech

# This script authenticates automatically using the GOOGLE_APPLICATION_CREDENTIALS
# environment variable you set in the terminal.
try:
    client = texttospeech.TextToSpeechClient()
    print("Authentication successful.")
except Exception as e:
    print(
        "Authentication failed. Make sure your GOOGLE_APPLICATION_CREDENTIALS environment variable is set correctly."
    )
    print(f"Error: {e}")
    exit()

# The SSML content you provided.
ssml_text = """
<speak>
    <p>Once upon a time, in a land filled with <emphasis level="strong">giggles</emphasis> and sunshine, lived a <emphasis level="moderate">big red button</emphasis>.</p>
    <p><s>This wasn't just any button; oh no!</s> <s>It was a <prosody pitch="high" volume="loud">giant</prosody>, <prosody pitch="high" volume="loud">round</prosody>, <prosody pitch="high" volume="loud">bright red</prosody> button, bigger than Willa's head!</s></p>
    <par>
        <media>
            <prosody rate="slow">It sat on a tiny hill, all alone, watching the clouds drift by.</prosody>
        </media>
        <media begin="0s" end="10s" fadeOutDur="2s" gainDb="-10.0">
            <seq>
                <audio src="https://storage.googleapis.com/cwsounds/mixkit/mixkit-lullaby-night-531.mp3" clipStart="0" clipEnd="10s"/>
            </seq>
        </media>
    </par>
    <p>One day, a little girl named Lily discovered the button. She gasped!</p>
    <p><s>"Wow!" she whispered.</s> <s>It was so big and shiny!</s></p>
    <par>
        <media>
            <prosody rate="moderate">Lily carefully touched the button, her fingertip tracing its smooth, cool surface.</prosody>
        </media>
        <media begin="0s" end="5s" gainDb="-15.0">
            <seq>
                <audio src="https://storage.googleapis.com/cwsounds/mixkit/mixkit-chillax-655.mp3" clipStart="0" clipEnd="5s"/>
            </seq>
        </media>
    </par>
    <p>Suddenly, the button began to <emphasis level="strong">glow</emphasis>!</p>
    <p><s>A soft, warm light pulsed from its center.</s> <s>Lily giggled, her eyes wide with wonder.</s></p>
    <par>
        <media>
            <prosody rate="fast">The button hummed, a low, happy sound, and then...<break time="1s"/> POP!</prosody>
        </media>
        <media begin="0s" end="3s" gainDb="-12.0">
            <seq>
                <audio src="https://storage.googleapis.com/cwsounds/mixkit/mixkit-loving-you-is-easy-1006%20%281%29.mp3" clipStart="0" clipEnd="3s"/>
            </seq>
        </media>
    </par>
    <p>A tiny, sparkly fairy appeared, fluttering around Lily's head!</p>
    <p><s>"Hello!" chirped the fairy.</s> <s>"I'm Fifi, and I live inside the button!"</s></p>
    <p>Lily and Fifi became the best of friends, playing hide-and-seek among the clouds and sharing sweet dreams under the big red button's warm glow.</p>
    <par>
        <media>
            <prosody rate="slow" pitch="low" volume="soft">And that, Willa, is the story of the big red button and its magical friend.</prosody>
        </media>
        <media begin="0s" end="15s" fadeOutDur="3s" gainDb="-8.0">
            <seq>
                <audio src="https://storage.googleapis.com/cwsounds/mixkit/mixkit-beautiful-dream-493.mp3" clipStart="0" clipEnd="15s"/>
            </seq>
        </media>
    </par>
</speak>
"""

# Set the text input to be synthesized
synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)

# Build the voice request, select a language code ("en-US") and a
# high-quality Wavenet voice.
voice_params = texttospeech.VoiceSelectionParams(
    language_code="en-US", name="en-US-Wavenet-F"
)

# Select the type of audio file you want returned
audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

print("Synthesizing speech from SSML...")
# Perform the text-to-speech request on the text input with the selected
# voice parameters and audio file type
response = client.synthesize_speech(
    input=synthesis_input, voice=voice_params, audio_config=audio_config
)

# The response's audio_content is binary.
output_filename = "output_story.mp3"
with open(output_filename, "wb") as out:
    # Write the response's audio content to a file.
    out.write(response.audio_content)
    print(f'Audio content written to file "{output_filename}"')
