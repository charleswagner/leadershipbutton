### ## Configuration Reference

The configuration system uses a two-tier approach:

1. **Default Configuration**: `.specpilot/engine/config_default.json` contains the base framework settings
2. **Project Override**: `.specpilot/workspace/config/config.json` (optional) contains project-specific overrides

**Configuration Loading Logic:**

- Load default configuration from `.specpilot/engine/config_default.json`
- If `.specpilot/workspace/config/config.json` exists, deeply merge its settings over the defaults
- Any setting in the workspace config takes precedence over the default

**DO NOT EDIT MANUALLY** - all configuration changes should be made through the framework engine.

#### Logging Configuration

- **`verbose_mode`** (boolean): Enable/disable detailed logging
- **`notepad_summary`** (string): Control notepad summary format for displaying actual notepad contents
  - `"one-line"`: Brief one-line summary of notepad contents at end of responses
  - `"command"`: Detailed command-style summary of notepad contents
  - `"none"`: Disable notepad summaries entirely
- **`track_model`** (boolean): Enable/disable model tracking

#### Commit Configuration

- **`commit_intelligence`** (boolean): Enable intelligent commit analysis
- **`session_analytics`** (boolean): Track development session metrics
- **`frustration_scoring`** (boolean): Analyze user frustration patterns
- **`productivity_metrics`** (boolean): Calculate productivity scores

#### Configuration Management

- **Engine Control**: All configuration changes are validated and applied by the framework engine
- **Single Source of Truth**: Configuration options are defined in this spec_driven_prompt.md file
- **Validation**: The engine ensures all configuration values are valid before applying changes
