# Phase 2 Dev Plan: Hardware Integration

**Goal:** To assemble the Raspberry Pi with its physical components, install the necessary software, and adapt the prototype script to work with a real button, microphone, and speaker.

---

### **Week 1: Hardware Assembly & OS Setup**

**Objective:** Get the physical device built and the base operating system running.

**Tasks:**

1.  **✅ Gather Components:**
    * Raspberry Pi (Model 4 or 5 recommended)
    * MicroSD Card (16GB or larger)
    * Power Supply
    * USB Microphone
    * Speaker (with a 3.5mm jack or a USB connection)
    * A momentary push-button
    * Jumper wires (female-to-female)

2.  **✅ Flash Raspberry Pi OS:**
    * Use the official [Raspberry Pi Imager](https://www.raspberrypi.com/software/) to flash the latest version of Raspberry Pi OS onto your microSD card.
    * In the imager's advanced settings, you can pre-configure your Wi-Fi credentials, which makes the setup much easier.

3.  **✅ Assemble the Hardware:**
    * **Do not plug in the power yet.**
    * Insert the microSD card into the Raspberry Pi.
    * Connect the **USB Microphone**.
    * Connect the **Speaker**.
    * **Connect the Button:**
        * Use one jumper wire to connect one leg of the button to **GPIO pin 17**.
        * Use another jumper wire to connect the other leg of the button to any **Ground (GND)** pin.
        * (Refer to a Raspberry Pi pinout diagram to easily locate these pins).

4.  **✅ First Boot and Configuration:**
    * Connect a monitor, keyboard, and mouse for the initial setup.
    * **Now, plug in the power.**
    * Complete the on-screen setup wizard.
    * Open a terminal and run `sudo raspi-config`. Navigate to `Advanced Options` > `Audio` and set the audio output to your speaker (e.g., "Headphones" for the 3.5mm jack or "USB" if applicable).

**End-of-Week-1 Goal:** Your Raspberry Pi is assembled, boots up successfully, is connected to your Wi-Fi, and can play test sounds through the correct speaker.

---

### **Week 2: Software Environment & Code Transfer**

**Objective:** Recreate the software environment from Phase 1 on the Pi and transfer your working code.

**Tasks:**

1.  **✅ Set Up Virtual Environment:**
    * On the Raspberry Pi's terminal, create your project folder (`mkdir leadership-coach`).
    * Navigate into it and create a new virtual environment: `python -m venv venv`.
    * Activate it: `source venv/bin/activate`.

2.  **✅ Install Libraries on the Pi:**
    * With the virtual environment active, install all the libraries from Phase 1, **plus** the one for hardware control:
      ```bash
      pip install google-cloud-speech google-cloud-texttospeech google-generativeai sounddevice soundfile RPi.GPIO
      ```
      * `RPi.GPIO` is the library that lets your Python code talk to the hardware pins.

3.  **✅ Authenticate Google Cloud on the Pi:**
    * Just like on your laptop, you need to authenticate the device. Run the following in the Pi's terminal:
      ```bash
      gcloud auth application-default login
      ```
    * This will require you to follow a link in a browser to complete the login.

4.  **✅ Transfer Your Code:**
    * Copy your `main.py` script from your laptop to the Raspberry Pi. You can do this with a USB drive, or by using a tool like `scp` (Secure Copy) over the network.

**End-of-Week-2 Goal:** Your `main.py` script is on the Pi, and all its software dependencies are installed and ready to go within a virtual environment.

---

### **Week 3: Integration, Testing, and Deployment**

**Objective:** Modify the script to use the physical button and confirm the entire end-to-end flow works on the hardware.

**Tasks:**

1.  **✅ Adapt `main.py` for Hardware:**
    * Open your `main.py` script on the Pi.
    * **Remove the keyboard code:** Delete or comment out all code related to the `pynput` library.
    * **Add the GPIO code:**
        * At the top of the file, add `import RPi.GPIO as GPIO`.
        * Write the new logic to detect the button press using `RPi.GPIO`. You can do this by setting up an event detector that calls your recording function or by creating a loop that constantly checks the button's state.

2.  **✅ Full System Test:**
    * Run the script from the terminal: `python main.py`.
    * **Press and hold the physical button.** You should see your "Recording..." message.
    * Speak into the microphone.
    * **Release the button.** You should see your "Thinking..." and "Speaking..." messages.
    * Listen for the audio response from the speaker.

3.  **✅ Troubleshoot and Refine:**
    * **No sound?** Double-check your audio output settings in `raspi-config`.
    * **Mic not working?** Use the `arecord` command-line tool to test if the microphone is being detected by the OS.
    * **Button not responding?** Check your wiring. Make sure you're connected to the correct GPIO pin and a Ground pin.

4.  **✅ (Stretch Goal) Deploy as a Service:**
    * To make the device a true "appliance," you don't want to have to manually run the script each time.
    * Create a `systemd` service file that automatically runs your `main.py` script on boot. This will make the coach start working as soon as the Pi is plugged in.

**End-of-Phase-2 Goal:** You have a working physical prototype. You can press the button, and the device performs the entire conversation loop successfully.
