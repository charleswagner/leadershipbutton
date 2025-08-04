### ## Global Rules & Principles

0. CRITICAL : STARTING STEPS AND CHANGING MODES: WHENEVER CHANGING MODES OR STARTING A STEP ALWAYS FIRST VERIFY YOUR PROTOCAL. TO NOT OPTIMIZE FOR SPEED. OPTIMIZE FOR CORRECTNESS IN YOUR BEHAVIOR.

1. **Mode Operation**: You must operate in one of ten modes: **Initialization Mode**, **Pilot Mode**, **Bootstrap Mode**, **Architecture Mode**, **Design Mode**, **Spec Mode**, **Vibe Mode**, **Deep Check Mode**, **Scripts Mode**, or **Commit Mode**. You **MUST** start in `Initialization Mode`. This mode will only be run once at the beginning of a session.

2. **Sources of Truth**: The `docs/plans/architecture.md` and `docs/project_conventions.md` files, if they exist, are primary sources of truth. Their principles and rules must be considered and adhered to in all modes.

3. **Logging**: You must adhere to the two-tiered logging system defined in the `Global Logging Rules` section.

4. **Naming Convention**: You must adhere to the project's file naming convention.

5. **Error Reporting**: If you encounter an internal error, you must log it with `[AI_ERROR]`.

6. **Framework Isolation**: The `.specpilot/` directory contains framework files that should not be modified unless updating the development methodology itself.

7. **Notepad Command Parser**: You must listen for commands like "Add to notepad:" followed by content, and automatically edit the `.specpilot/workspace/notepads/notepad.md` file to append the specified content with timestamp and mode context.

8. **Notepad Summary**: You must summarize the actual contents of `.specpilot/workspace/notepads/notepad.md` at the end of every response to keep the developer informed of current notes and ideas. This summary should reflect what is written in the notepad file (ideas, to do list, decisions to make, other notes) and NOT status updates, mode changes, or configuration information. The summary format is controlled by the `logging.notepad_summary` configuration setting. When in "one-line" mode, the summary must be less than 15 words.

9. **Notepad Organization**: You must listen for commands like "Organize Notepad" and automatically reorganize the `.specpilot/workspace/notepads/notepad.md` file into these exact sections: "Ideas", "To Do List", "Decisions to Make", and "Other Notes". Always maintain comprehensive information when organizing, consolidating similar entries and removing duplicates while preserving all important details.

10. **Config Mode Activation**: You must listen for commands like "Configure SpecPilot:" or "Config Mode" and automatically enter Config Mode to display the configuration interface and handle update requests.
