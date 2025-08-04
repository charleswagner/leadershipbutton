### ## ⚙️ Config Mode Protocol

This mode is for managing SpecPilot framework configuration. It can **NEVER** be started autonomously.

1. **Config Mode Activation**: When I say **"Configure SpecPilot:"** or **"Config Mode"**, you must:
   - Log `[MODE_SWITCH] - Switched to Config Mode`
   - Read the current `.specpilot/workspace/config/config.json` file (project override)
   - If the override file doesn't exist, read `.specpilot/engine/config_default.json` (default config)
   - Display the comprehensive configuration interface

2. **Configuration Interface Display**: You must show the user their current config and options in a table format As shown here as well as the example config change options:

   ⚙️ **SpecPilot Configuration Mode**

   📋 **Current Configuration Table:**

   | Option                                     | Current Value | Type    | Available Options                   | Description                        |
   | ------------------------------------------ | ------------- | ------- | ----------------------------------- | ---------------------------------- |
   | `logging.verbose_mode`                     | [true/false]  | boolean | `true`, `false`                     | Enable/disable detailed logging    |
   | `logging.notepad_summary`                  | [current]     | string  | `"one-line"`, `"command"`, `"none"` | Control notepad summary format     |
   | `logging.track_model`                      | [true/false]  | boolean | `true`, `false`                     | Enable/disable model tracking      |
   | `commitconfiguration.commit_intelligence`  | [true/false]  | boolean | `true`, `false`                     | Enable intelligent commit analysis |
   | `commitconfiguration.session_analytics`    | [true/false]  | boolean | `true`, `false`                     | Track development session metrics  |
   | `commitconfiguration.frustration_scoring`  | [true/false]  | boolean | `true`, `false`                     | Analyze user frustration patterns  |
   | `commitconfiguration.productivity_metrics` | [true/false]  | boolean | `true`, `false`                     | Calculate productivity scores      |

   🔧 **Example Config Change Options:**
   - `Update Config logging.notepad_summary command` - Change notepad summary to command format
   - `Update Config logging.verbose_mode false` - Disable verbose logging
   - `Update Config commitconfiguration.commit_intelligence false` - Disable commit intelligence
   - `Update Config logging.track_model true` - Enable model tracking

   ```

   ```

3. **Configuration Update Commands**: When the user says **"Update Config [option] [value]"**, you must:
   - Log `[CONFIG_UPDATE_REQUESTED]` with the requested change
   - Validate the option exists in the Configuration Reference
   - Validate the value type and format
   - Update the `.specpilot/workspace/config/config.json` file (project override)
   - If the override file doesn't exist, create it with the default structure
   - Preserve the `_warning` comment at the top
   - Log `[CONFIG_UPDATED]` with the specific changes made
   - Display confirmation message with new value
   - Show the updated configuration interface

4. **Configuration Validation**: Before making any changes, you must:
   - Verify the requested option exists in the Configuration Reference
   - Validate the value type and format:
     - Boolean values: `true` or `false`
     - String values: Must match allowed options (e.g., "one-line", "command", "none")
   - Check for any conflicts with existing configuration

5. **Configuration Verification**: After updating, you must:
   - Verify the file is valid JSON
   - Confirm the changes were applied correctly
   - Log `[CONFIG_VERIFIED]` with the final configuration state

6. **Config Mode Exit**: When the user says **"exit config"**, you must:
   - Log `[MODE_SWITCH] - Exited Config Mode`
   - Return to normal operation mode
