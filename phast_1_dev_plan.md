# Phase 1 Dev Plan: Laptop Prototype

**Goal:** To create a fully functional software prototype on a laptop that captures audio via a key press, processes it through Google's AI services, and plays back a spoken response.

---

### **Week 1: Setup and Core Recording**

**Objective:** Prepare the development environment and successfully record audio triggered by a keyboard key.

**Tasks:**

1.  **✅ Environment Setup:**
    * Install Python 3.9 or later from [python.org](https://python.org).
    * Create a new project folder (e.g., `leadership-coach`).
    * Open a terminal in that folder and create a virtual environment:
        ```bash
        python -m venv venv
        ```
    * Activate the virtual environment:
        * **macOS/Linux:** `source venv/bin/activate`
        * **Windows:** `venv\Scripts\activate`

2.  **✅ Install Libraries:**
    * With your virtual environment active, run the following command to install all necessary libraries at once:
        ```bash
        pip install google-cloud-speech google-cloud-texttospeech google-generativeai sounddevice soundfile pynput
        ```
        * `sounddevice` & `soundfile`: For recording and saving audio.
        * `pynput`: For detecting keyboard presses easily.

3.  **✅ Google Cloud Setup:**
    * Install the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install).
    * Log in to your account from the terminal:
        ```bash
        gcloud auth application-default login
        ```
    * In your Google Cloud Console (browser), ensure the following APIs are **enabled** for your project:
        * Cloud Speech-to-Text API
        * Cloud Text-to-Speech API
        * Vertex AI API (for Gemini)

4.  **✅ Create the Initial Script (`main.py`):**
    * Create a file named `main.py`.
    * Write the initial code to listen for a key press (e.g., the `space` bar) and print messages like "Recording started..." on key press and "Recording stopped..." on key release. Use the `pynput` library for this.

5.  **✅ Implement Audio Recording:**
    * Integrate `sounddevice` into your script.
    * When the key is pressed, start recording audio from your laptop's microphone into a buffer.
    * When the key is released, stop the recording and use the `soundfile` library to save the buffered audio to a file named `output.wav`.

**End-of-Week-1 Goal:** You can run `python main.py`, press and hold the space bar to record your voice, and see an `output.wav` file appear in your project folder when you release it.

---

### **Week 2: API Integration and Full Loop**

**Objective:** Connect the recorded audio to the full chain of Google Cloud APIs to get a spoken response.

**Tasks:**

1.  **✅ Function 1: `transcribe_audio()`**
    * In `main.py`, create a function that takes `output.wav` as input.
    * Inside this function, write the code to call the **Google Speech-to-Text API**.
    * Have it return the transcribed text as a string.
    * Add print statements to show the transcript in the terminal for debugging.

2.  **✅ Function 2: `get_advice()`**
    * Create a function that takes the transcribed text as input.
    * Inside, define your master prompt for **Gemini**. Start with the example from the PRD.
    * Call the Gemini API with the prompt and get the AI-generated advice back.
    * Return the advice text as a string.

3.  **✅ Function 3: `synthesize_speech()`**
    * Create a function that takes the advice text from Gemini as input.
    * Inside, call the **Google Text-to-Speech API**.
    * Configure it with a voice you like (e.g., `en-US-Journey-D`).
    * Save the resulting audio content to a file named `response.mp3`.

4.  **✅ Function 4: `play_audio()`**
    * Create a simple function that uses `sounddevice` and `soundfile` to play the `response.mp3` file through your laptop speakers.

5.  **✅ Assemble the Main Loop:**
    * In your main execution block, chain all the functions together.
    * After the recording stops, call `transcribe_audio()`, then pass its result to `get_advice()`, then pass *its* result to `synthesize_speech()`, and finally call `play_audio()`.
    * Add user-friendly print statements for each step: `Listening...`, `Thinking...`, `Speaking...`.

**End-of-Week-2 Goal:** You can run the script, record a question, and hear a computer-generated voice respond through your speakers.

---

### **Week 3: Refinement and Polish**

**Objective:** Fine-tune the user experience and prepare the code for the transition to hardware.

**Tasks:**

1.  **✅ Prompt Engineering:**
    * This is the most creative and critical part. Run the script dozens of time with different questions.
    * Tweak the master prompt in your `get_advice()` function. Experiment with the persona, tone, and constraints. Try different leadership styles (e.g., "empathetic," "decisive," "creative").
    * Your goal is to get consistently high-quality, safe, and helpful responses.

2.  **✅ Voice Selection:**
    * Browse the [Google Cloud Text-to-Speech voice library](https://cloud.google.com/text-to-speech/docs/voices).
    * Try out different voices in your `synthesize_speech()` function until you find the perfect one for your coach.

3.  **✅ Error Handling:**
    * Add `try...except` blocks around each API call. What happens if the internet is down? What if Speech-to-Text can't understand the audio?
    * Print friendly error messages (e.g., "Sorry, I couldn't understand that. Please try again.").

4.  **✅ Code Cleanup:**
    * Add comments to your code explaining what each function does.
    * Ensure your variables have clear names.
    * Organize your code logically.

**End-of-Phase-1 Goal:** You have a robust, well-commented Python script that reliably performs the entire conversation loop and is ready to be moved to the Raspberry Pi in Phase 2.
