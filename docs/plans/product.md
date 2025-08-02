# Product Requirements Document: The Leadership & EQ Coach

**Version:** 1.0
**Date:** August 2, 2025
**Author:** Chrles Wagner

---

## 1. Vision & Mission

### 1.1. Vision

To create a tangible, interactive tool that helps children develop foundational leadership and emotional intelligence (EQ) skills by providing personalized, on-demand guidance in a voice they trust.

### 1.2. Mission

We are building a simple hardware device—a Raspberry Pi with a button, microphone, and speaker—that allows a child to describe a real-life situation and receive a conversational, age-appropriate response. This response will be crafted based on a pre-defined leadership style (e.g., empathetic, decisive, collaborative) to model effective communication and problem-solving.

---

## 2. User Persona

**Name:** Alex
**Age:** 8-12 years old
**Goals:**

- To understand how to handle tricky social situations with friends and at school.
- To feel more confident when making decisions.
- To learn how to be a good friend and a fair leader in group activities.
  **Frustrations:**
- Doesn't always know the "right thing" to say or do.
- Sometimes feels overwhelmed by social conflicts (e.g., disagreements over games, feeling left out).
- Wants to ask for advice but might feel embarrassed to talk to an adult about every little thing.

---

## 3. Core User Journey

1.  **The Situation:** Alex faces a challenge. For example, "My friend and I both want to be the captain of our soccer team, and we're arguing about it."
2.  **The Interaction:** Alex picks up the device, **presses and holds the button**, and speaks into the microphone, explaining the situation in their own words.
3.  **The Release:** When finished, Alex **releases the button**. This signals the end of the recording.
4.  **The Magic:** The device processes the request.
5.  **The Guidance:** After a short pause, the device's speaker plays an audio response in the pre-selected "leader's voice." The advice is constructive and aligned with the chosen leadership style. For example: _"It sounds like a tough spot to be in. A good leader knows that teamwork is more important than being the captain. Have you thought about suggesting that you and your friend could be co-captains? Or maybe one of you could be captain and the other could be in charge of leading warm-ups. That way, you both get to lead."_
6.  **The Reflection:** Alex thinks about the advice and how to apply it.

---

## 4. Key Features & Technical Flow

### 4.1. Hardware Interface (The "Box")

- **Input:** A single, large, durable push-button.
- **Audio Input:** An integrated microphone.
- **Audio Output:** An integrated speaker.
- **Platform:** Raspberry Pi.

### 4.2. Voice Recording & Transcription

- **Trigger:** The system starts recording audio when the button is pressed and held.
- **Action:** The recording stops upon button release and is saved locally as a temporary audio file (e.g., `.wav`).
- **Service:** The audio file is sent to the **Google Cloud Speech-to-Text API** to be converted into a text transcript.

### 4.3. AI-Powered Advice Generation

- **Input:** The text transcript from the Speech-to-Text API.
- **Core Logic:** The transcript is inserted into a master prompt that is sent to the **Gemini API**.
- **The Master Prompt:** This is a carefully crafted prompt that includes:
  - The chosen leadership style and voice persona.
  - Instructions to provide age-appropriate, constructive, and safe advice.
  - The user's transcribed text.
  - **Example Prompt Structure:**

    ```
    You are a wise and [empathetic] leadership coach speaking to an 8-year-old. Your name is [Coach's Name] and you speak in a [calm and encouraging] tone. A child has come to you with a problem.

    The child said: "[INSERT TRANSCRIBED TEXT HERE]"

    Your goal is to provide a short, helpful, and safe response that models [empathetic leadership]. Do not give complex advice. Focus on understanding feelings, fairness, and teamwork. Your response should be no more than 3-4 sentences.
    ```

- **Output:** The Gemini API returns a text response.

### 4.4. Personalized Voice Output

- **Input:** The text response from the Gemini API.
- **Service:** The text is sent to the **Google Cloud Text-to-Speech API**.
- **Configuration:** The API is configured to use a pre-selected voice that matches the desired persona.
- **Action:** The API returns an audio file, which is then played through the device's speaker.

### 4.5. Data & Logging (Optional V1.1 Feature)

- **Service:** **Firebase Firestore**.
- **Functionality:**
  - Log the anonymized transcript and the AI-generated response for review.
  - Create a simple user profile to track the number of interactions over time.
  - **Privacy Note:** All data storage must be handled with strict privacy controls.

---

## 5. Success Metrics

- **Engagement:** The child uses the device regularly (e.g., more than once a week).
- **Qualitative Feedback:** The child can articulate how the device has helped them think through a problem.
- **Parental Feedback:** Parents observe positive changes in their child's approach to social situations and decision-making.

---

## 6. Future Ideas (Post-V1)

- **Multiple Leadership Styles:** Allow the child to switch between different coach personas (e.g., "The Diplomat," "The Innovator," "The Cheerleader").
- **Follow-up Questions:** Enable the AI to ask clarifying questions if the initial description is unclear.
- **"Memory":** Allow the coach to reference past conversations to provide more contextual advice (requires careful privacy and data management).
- **Parent Dashboard:** A simple web interface for a parent to review interactions and update the master prompt.
