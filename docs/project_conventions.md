# Project Conventions

This document is the official source of truth for all development standards in this project.

### The "Golden Thread": File Naming & Location

To maintain clarity, every feature must follow a strict naming and location convention that creates a "golden thread" from specification to implementation to verification.

| Artifact          | Location              | Naming Convention        | Purpose                                                     |
| :---------------- | :-------------------- | :----------------------- | :---------------------------------------------------------- |
| **Specification** | `docs/specs/`         | `spec_[feature_name].md` | The detailed blueprint for a feature. The source of truth.  |
| **Source Code**   | `src/[project_name]/` | `[feature_name].py`      | The implementation that directly fulfills the spec.         |
| **Test File**     | `tests/`              | `test_[feature_name].py` | The code that verifies the implementation against the spec. |

### The `.specpilot/` Framework Directory: Engine vs. Artifacts

It is critical to understand the separation between the project's own files and the framework used to build it.

- **Project Files (`src/`, `docs/`, `tests/`):** Think of these as the **Products & Blueprints** created in a factory. They are the direct output of our development work.
- **Framework Files (`.specpilot/`):** Think of this as the **Factory Machinery & Schematics**. This is the tooling and the set of instructions that runs the factory itself. You don't mix machine parts with the finished products.

#### Contents and Usage

The `.specpilot/` directory contains the core files that define the agent's behavior.

| File / Directory        | Purpose                                                                       | How & When to Use                                                                                                                   |
| :---------------------- | :---------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------- |
| `config.json`           | Configures `specpilot` runtime behavior (e.g., commit intelligence, logging). | **DO NOT EDIT MANUALLY** - Configuration managed by the engine. See `.specpilot/engine/spec_driven_prompt.md` for options.          |
| `spec_driven_prompt.md` | The core "constitution" defining the agent's modes, rules, and protocols.     | **DO NOT EDIT** unless you are making a fundamental change to the development methodology. This is the "source code" for the agent. |

### Commit Configuration and Log Analysis

The `commitconfiguration` section in `.specpilot/workspace/config/config.json` (project override) controls how the framework analyzes development sessions and generates intelligent commit messages.

#### Configuration Options:

- **`commit_intelligence`**: Enable/disable intelligent commit message generation
- **`session_analytics`**: Track development session metrics and patterns
- **`frustration_scoring`**: Analyze user frustration patterns from conversation logs
- **`productivity_metrics`**: Calculate productivity scores based on development activities

#### Log Analysis Process:

1. **Automatic Logging**: Framework continuously logs all interactions to `.specpilot/workspace/logs/`
2. **Commit Mode Analysis**: When entering Commit Mode, framework analyzes both log files:
   - `.specpilot/workspace/logs/specpilot.log` (milestone events)
   - `.specpilot/workspace/logs/specpilot_verbose.log` (complete transcripts)
3. **Intelligence Generation**: Based on log analysis, generates:
   - Development intelligence scores (frustration, productivity, agent effectiveness, vibe)
   - Session statistics and performance metrics
   - Hybrid commit messages with traditional format + intelligence appendix

#### Configuration Management:

- **Engine Control**: All configuration changes are managed by the SpecPilot engine
- **Reference Documentation**: See `.specpilot/engine/spec_driven_prompt.md` for all available options
- **Validation**: The engine validates all configuration changes before applying them
- **DO NOT EDIT MANUALLY**: The `.specpilot/workspace/config/config.json` file should not be edited directly (use Config Mode)

#### Usage:

- **Enable Features**: Configuration is managed through the framework engine
- **Customize Analysis**: All options documented in the engine specification
- **Review Logs**: Check `.specpilot/workspace/logs/` for development audit trail
- **Commit Mode**: Use "Prepare a commit" command to trigger intelligent analysis
