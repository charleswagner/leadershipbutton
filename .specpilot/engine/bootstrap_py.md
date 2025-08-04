# Python Project Bootstrap Checklist

This document is the master checklist for setting up a new, professional, spec-driven Python project environment. Follow these steps in order.

---

### Step 1: Initial Folder and Git Setup

1.  Create the root directory for your new project.
    ```bash
    mkdir new_project_name
    cd new_project_name
    ```
2.  Initialize a Git repository.
    ```bash
    git init
    ```

---

### Step 2: Configure the Cursor AI Environment

1.  Open the project in Cursor.
2.  Open the Chat Panel (`Cmd+K` or `Ctrl+K`).
3.  Click the mode selector dropdown (e.g., "Agent") and choose to create a **New Mode**.
4.  Name the mode **"Spec-Driven Python"**.
5.  Find your master `spec_driven_prompt.md` file (the one we created with all the modes and rules).
6.  **Copy the entire contents** of that master prompt file.
7.  **Paste the contents** into the "Instructions" box for your new "Spec-Driven Python" mode.
8.  Ensure all "Auto-run" and "Auto-apply" settings are **turned OFF**.
9.  Click "Done" to save the mode.

---

### Step 3: Create Core Configuration Files

Create the following files in the project's root directory. You can leave them empty for now; the AI Bootstrap process will populate some of them.

1.  `.cursor-rules.json`
2.  `.gitignore`
3.  `requirements.txt`
4.  `README.md`
5.  `.pre-commit-config.yaml` (Paste the full configuration with `black`, `flake8`, and `prettier` into this file).

---

### Step 4: Set Up the Python Environment and Quality Tools

1.  Install all the necessary development tools using the robust `python3 -m pip` command.
    ```bash
    python3 -m pip install pre-commit black flake8 prettier
    ```
2.  Activate the pre-commit hooks for this repository.
    ```bash
    python3 -m pre_commit install
    ```
    You should see a confirmation message.

---

### Step 5: Run the AI Bootstrap Process

You are now ready to have the AI build the project structure.

1.  In the Cursor chat, ensure your **"Spec-Driven Python"** mode is active.
2.  Send your first message to enter Bootstrap Mode:
    ```
    Enter Bootstrap Mode
    ```
3.  Send your second message, which is the project brief. This can be a simple description or a detailed plan.

    ```
    Bootstrap new project

    [...paste your entire project idea or development plan here...]
    ```

4.  The AI will now propose the creation of the full directory structure and all the initial files.
5.  **Review the AI's plan carefully.**
6.  Once you approve it, the project structure will be built, and you will be automatically switched to **Design Mode**, ready to begin your first task.
