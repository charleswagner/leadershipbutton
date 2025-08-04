# Project Conventions

This document is the official source of truth for all development standards in this project.

## Testing Conventions

### CRITICAL RULE: No Business Logic in Tests

**Tests must contain ONLY orchestration and verification logic. Business logic belongs exclusively in the main codebase.**

#### ✅ What Tests SHOULD Contain:

- **Orchestration Logic**: Setting up test scenarios, mocking dependencies, calling methods
- **Verification Logic**: Assertions, comparisons, validation of expected outcomes
- **Test Infrastructure**: Helper methods for test setup, data creation, cleanup
- **Mock Configuration**: Defining mock behaviors and responses

#### ❌ What Tests MUST NEVER Contain:

- **Duplicate Business Logic**: Re-implementing main application functionality
- **Alternative Implementations**: Different ways of achieving the same business outcome
- **Production Algorithms**: Core processing logic that should be in main code
- **Configuration Logic**: Business rules about how the system should behave

#### Examples of PROHIBITED Test Patterns:

```python
# ❌ BAD: Test contains business logic (audio processing)
def test_audio_processing(self):
    # This duplicates business logic from main code
    sample_rate = 24000  # Should come from centralized config
    audio_data = self.process_audio_manually(raw_bytes, sample_rate)
    self.assertEqual(audio_data.sample_rate, 24000)

# ✅ GOOD: Test only orchestrates and verifies
def test_audio_processing(self):
    # Only orchestration and verification
    audio_result = self.api_client.text_to_speech("test")
    self.assertEqual(audio_result.sample_rate, 24000)
```

#### Testing Anti-Patterns to AVOID:

1. **Testing Theater**: Tests that print verbose output or "guidance" instead of asserting
2. **Manual Interaction Tests**: Tests requiring human input (spacebar, keyboard interaction)
3. **Business Logic Duplication**: Tests that re-implement main application functionality
4. **Integration Wrapping**: Tests that just wrap the main application without adding value
5. **Complex Test Logic**: Tests with threading, timeouts, or complex setup (test the wrong thing)

#### Proper Test Strategy:

1. **Unit Tests**: Test individual functions/methods with clear inputs and expected outputs
2. **Integration Tests**: Run actual application components together, verify interactions
3. **Mock-Based Tests**: Use mocks to isolate components and test specific behaviors
4. **Error Scenario Coverage**: Test how components handle various error conditions
5. **Manual Testing**: For complex integration scenarios, run the actual application

#### Centralized Configuration Rule:

- **Tests and main code MUST use the same configuration sources**
- **No duplicate configuration paths between test and production code**
- **All configuration should come from centralized managers/configs**
- **Tests should never define their own business configuration values**

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
