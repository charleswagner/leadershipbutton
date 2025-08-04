# LeadershipButton

(A brief, one-sentence description of what the LeadershipButton project does will go here.)

### ✨ Spec-Driven Development

This project is built using a **Spec-Driven Development** methodology, orchestrated by the `specpilot` framework. All new functionality must begin as a detailed markdown **specification file** located in the `docs/specs/` directory.

This approach ensures that every feature is well-defined, testable, and aligned with our goals before any code is written. The spec is the source of truth.

### 📂 Project Structure

We enforce a strict separation of concerns between the **application code** (`src`, `tests`) and the **project artifacts** (`docs`). The entire process is orchestrated by the `specpilot` framework, which is embedded in its own directory with a clean, organized structure.

```
.
├── .specpilot/                    # The embedded framework engine
│   ├── engine/                    # Core framework files
│   │   ├── spec_driven_prompt.md  # Master protocol (AI assistant "constitution")
│   │   └── bootstrap_py.md        # Development environment setup guide
│   ├── config/                # Project-specific overrides
│   │   ├── config.json        # (Optional) Project config override
│   │   └── spec_driven_prompt_override.md # (Optional) Project prompt override
│   ├── notepads/              # Developer notes
│   │   └── notepad.md         # Developer scratchpad and notes
│   └── logs/                  # Runtime logs
│       ├── specpilot.log      # Milestone log (high-level progress)
│       └── specpilot_verbose.log # Verbose log (complete transcripts)
├── docs/                          # Project documentation
│   ├── plans/                     # Project planning documents
│   ├── specs/                     # Feature specifications
│   └── project_conventions.md     # Development standards
├── src/                           # Application source code
└── tests/                         # Automated tests
```

### 🔧 Framework Components

**Engine Files** (`.specpilot/engine/`): The core "brain" of the framework

- **`spec_driven_prompt.md`**: Master protocol defining AI assistant behavior, modes, and rules
- **`bootstrap_py.md`**: Complete setup guide for new development environments

**Configuration Override** (`.specpilot/workspace/config/`): Project-specific overrides

- **`config.json`**: Project-specific configuration that overrides defaults
- **`spec_driven_prompt_override.md`**: Project-specific prompt rules that take precedence

**Workspace** (`.specpilot/workspace/`): Runtime files that change during development

- **`notepads/notepad.md`**: Persistent developer scratchpad for notes and ideas
- **`logs/`**: Development audit trail and conversation history

**Configuration** (`.specpilot/engine/config_default.json`): Default framework settings

- Controls logging behavior and commit intelligence features
- **Commit Configuration**: Customize commit analysis, scoring, and intelligence features
- **Log Analysis**: Framework automatically analyzes `.specpilot/workspace/logs/` for commit intelligence
