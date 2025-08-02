# Phase 3 Dev Plan: From Prototype to Product

**Goal:** To transform the working hardware prototype into a durable, standalone "appliance" by creating an enclosure and making the software run automatically.

---

### **Week 1: Automating the Software**

**Objective:** To make the Python script run automatically on boot, turning the Raspberry Pi into a dedicated device that doesn't require manual intervention.

**Tasks:**

1.  **✅ Final Code Review:**
    * Review your `main.py` script. Ensure all comments are clear and any debugging `print()` statements that are no longer needed have been removed.
    * Add robust `try...except` blocks around the entire main loop to ensure that if one API call fails, the script doesn't crash and can be ready for the next button press.

2.  **✅ Create a Systemd Service File:**
    * In the Pi's terminal, create a new service file:
        ```bash
        sudo nano /etc/systemd/system/coach.service
        ```

3.  **✅ Configure the Service:**
    * Paste the following configuration into the `coach.service` file. Be sure to replace `pi` with your actual username if it's different.
        ```ini
        [Unit]
        Description=Leadership Coach Service
        After=network.target

        [Service]
        ExecStart=/home/pi/leadership-coach/venv/bin/python /home/pi/leadership-coach/main.py
        WorkingDirectory=/home/pi/leadership-coach
        StandardOutput=inherit
        StandardError=inherit
        Restart=always
        User=pi

        [Install]
        WantedBy=multi-user.target
        ```

4.  **✅ Enable and Test the Service:**
    * Save and close the file.
    * Reload the systemd daemon to make it aware of your new service:
        ```bash
        sudo systemctl daemon-reload
        ```
    * Enable the service to start on boot:
        ```bash
        sudo systemctl enable coach.service
        ```
    * Start the service immediately to test it:
        ```bash
        sudo systemctl start coach.service
        ```
    * Check its status to see if it's running without errors:
        ```bash
        sudo systemctl status coach.service
        ```
    * **The Real Test:** Reboot the Raspberry Pi (`sudo reboot`). Once it restarts, the script should be running automatically. Try pressing the button to see if it works without you doing anything in the terminal.

**End-of-Week-1 Goal:** The device is a true appliance. It runs the leadership coach application automatically after being powered on.

---

### **Week 2: Enclosure Design & Printing**

**Objective:** To design and 3D print a custom case that safely houses all components and is user-friendly.

**Tasks:**

1.  **✅ Measure Everything:**
    * Use digital calipers or a ruler to get the precise dimensions of the Raspberry Pi, the mounting holes, the speaker, the microphone, and the push-button.

2.  **✅ Design the Enclosure (CAD):**
    * Use a beginner-friendly CAD program like [Tinkercad](https://www.tinkercad.com/) or a more advanced one like Fusion 360.
    * Design a two-part case (a base and a lid).
    * **Critical Design Features:**
        * Openings for the USB-C power port and the USB microphone.
        * A hole in the top for the push-button.
        * A grill or series of small holes over the speaker for sound to escape.
        * Small holes for the microphone to pick up sound clearly.
        * Internal posts or standoffs that align with the Raspberry Pi's mounting holes to secure it.

3.  **✅ Print the First Prototype:**
    * Slice your CAD model and 3D print the first version of the enclosure. Use a low-quality/fast setting, as this is just for test fitting.

4.  **✅ Test Fit:**
    * Carefully place all the components into the printed case. Does everything fit? Are the ports aligned? Can you press the button easily? Take notes on what needs to change.

**End-of-Week-2 Goal:** You have a 3D-printed prototype case and a list of adjustments needed for the final version.

---

### **Week 3: Final Assembly & User Testing**

**Objective:** To assemble the final, polished device and get feedback from its intended user.

**Tasks:**

1.  **✅ Refine and Print Final Enclosure:**
    * Go back to your CAD software and make the adjustments from your test fit.
    * Print the final version of the enclosure on a higher quality setting.

2.  **✅ Final Assembly:**
    * Sand any rough edges on the  printed parts to make them smooth and safe for a child to handle.
    * Carefully place all components into the final enclosure.
    * Use small screws to secure the Raspberry Pi to the mounting posts and to fasten the lid to the base.

3.  **✅ The First User Test:**
    * Present the finished device to your child.
    * Give them a simple explanation of what it is and how to use it ("When you have a question or a story, just press and hold the button to talk to the coach.").
    * Observe them using it. Don't interfere.
    * **Listen to their feedback:** Is the voice clear? Is the advice helpful? Is it fun to use?

4.  **✅ Final Software Tweaks:**
    * Based on your observations, you might want to make small final changes to the software. For example:
        * Shorten the "Thinking..." time if it feels too long.
        * Adjust the speaker volume.
        * Make a minor tweak to the AI's persona in the prompt based on your child's reaction.

**End-of-Phase-3 Goal:** You have a fully assembled, durable, and kid-tested Leadership & EQ Coach device.
