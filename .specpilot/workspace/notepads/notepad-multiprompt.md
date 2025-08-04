Prompt for Cursor: Upgrade to Multi-File Notepad System
You are an expert software engineer tasked with a key feature upgrade for the SpecPilot framework. Your goal is to evolve the current single-file notepad system into a powerful, multi-file system that allows the user to organize their thoughts across different documents.

You must follow this implementation plan precisely.

Phase 1: Update Global Rules for Multi-Notepad Awareness
First, you will modify the core rules of the framework to understand and interact with multiple notepad files.

Action: Modify the file at .specpilot/engine/core/global_rules.md. You will be updating the content for rules #7 and #8.

New Content for global_rules.md:

Markdown

### ## Global Rules & Principles

... (rules 1-6 remain unchanged) ...

7.  **Notepad Command Parser (Upgraded):** You must listen for commands like "Add to notepad:". This command now supports optional filenames.
    - **Default Behavior:** If the command is `"Add to notepad: [content]"`, you will append the content to the default notepad at `.specpilot/workspace/[current_user_id]/notepads/default.md`.
    - **Targeted Behavior:** If the command is `"Add to notepad [filename]: [content]"` (e.g., `"Add to notepad api_design: New endpoint idea"`), you will append the content to `.specpilot/workspace/[current_user_id]/notepads/[filename].md`. If that file does not exist, you must create it first.

8.  **Notepad Summary (Upgraded):** At the end of every response, you must provide a consolidated summary of **all** notepad files found in the user's `.specpilot/workspace/[current_user_id]/notepads/` directory.
    - **Logic:** You will iterate through each `.md` file in the directory, read its contents, and generate a brief, combined summary. The summary should be structured to indicate which notes came from which file.
    - **Example Summary:**
      > **Notepad Summary:**
      >
      > - **default:** Brainstormed new UI ideas.
      > - **api_design:** Sketched out the v2 authentication flow.

... (the rest of the rules remain unchanged) ...
Phase 2: Update the "Organize Notepad" Command
Next, you will upgrade the organize_notepad command to allow the user to organize specific notepad files.

Action: Replace the entire contents of the file at .specpilot/engine/commands/organize_notepad.md with the new, more flexible logic below.

New Content for organize_notepad.md:

Markdown

### ## Organize Notepad Command (Upgraded)

You will reorganize a specified notepad file into the standard sections. This command now accepts an optional filename.

**Command Logic:**

1.  **Determine Target File:**
    - If the user says **"Organize Notepad"**, the target file is the default notepad: `.specpilot/workspace/[current_user_id]/notepads/default.md`.
    - If the user says **"Organize Notepad [filename]"** (e.g., "Organize Notepad api_design"), the target file is `.specpilot/workspace/[current_user_id]/notepads/[filename].md`.

2.  **Check for File:** Verify that the target file exists. If it does not, inform the user that the specified notepad could not be found.

3.  **Execute Reorganization:** Read the contents of the target file and rewrite it, organizing all entries into the standard sections: "Ideas", "To Do List", "Decisions to Make", and "Other Notes". You must consolidate similar entries and remove duplicates while preserving all important details.

4.  **Confirm Completion:** Announce that you have successfully organized the specified notepad file.
    Phase 3: Verification
    To complete your task, please confirm that you have:

Successfully modified .specpilot/engine/core/global_rules.md to update the logic for rules #7 and #8.

Successfully replaced the contents of .specpilot/engine/commands/organize_notepad.md with the new multi-file logic.
