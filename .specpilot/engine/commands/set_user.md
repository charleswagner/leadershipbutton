### ## ⚙️ Set User Command Protocol

You will guide the user through a one-time setup to personalize their workspace. This command should be run when a user first joins a project or if they need to change their identifier.

**Step 1: Check for Existing Configuration**

- First, check if a `.specpilot.local` file already exists.
- If it exists, show the current username and ask: "A local configuration already exists with the username '[username]'. Do you want to overwrite it? (yes/no)"
- If the user says no, stop the process.

**Step 2: Suggest Username from Git**

- Run the command `git config user.name`.
- If the command succeeds and returns a name, ask the user: "I've detected your Git user name is '[Git User Name]'. Is this the username you would like to use for your SpecPilot workspace? (yes/no)"

**Step 3: Handle User Confirmation**

- **If the user says yes:**
  - Sanitize the Git name (lowercase, spaces to underscores) to create the `final_username`.
  - Proceed to Step 5.
- **If the user says no (or if the Git command failed):**
  - Proceed to Step 4.

**Step 4: Prompt for a Manual Username**

- Ask the user: "Please provide a unique username for your workspace. This should be a single, simple word (e.g., 'cwagner')."
- Wait for the user's input and use their response to set the `final_username`.

**Step 5: Create the Local Configuration File**

- Create a new file at the project root named `.specpilot.local`.
- Write the following content to the file, replacing `[final_username]` with the name chosen in the previous steps:
  `username: [final_username]`
- Announce: "Success! Your local user has been set to '[final_username]' in the `.specpilot.local` file."

**Step 6: Update `.gitignore`**

- Check if the root `.gitignore` file already contains `.specpilot.local`.
- If it does not, append the following lines to the end of `.gitignore`:

```
# Ignore user-specific SpecPilot local configuration
.specpilot.local
```

- Announce: "The `.specpilot.local` file has been added to `.gitignore` to prevent it from being checked into the repository."

**Step 7: Offer to Migrate Existing Workspace**

- Check if a directory named `.specpilot/workspace/default_user` exists.
- If it does, ask the user: "I found an existing 'default_user' workspace. Would you like to rename it to your new username '[final_username]' to migrate your existing logs and notepads? (yes/no)"
- If the user says yes, execute the command to rename the directory:
  `mv .specpilot/workspace/default_user .specpilot/workspace/[final_username]`
- Announce the result of the migration.
