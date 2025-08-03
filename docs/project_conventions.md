# Project Conventions

This document serves as the primary source of truth for all documentation standards, file naming conventions, and project structure rules.

## 📁 Canonical Directory Structure

The consolidated and standardized directory structure for this project is:

```
project_root/
├── .specpilot/
│   ├── spec_driven_prompt.md           # AI assistant operational protocols
│   └── bootstrap_py.md                 # Development environment setup checklist
├── docs/
│   ├── plans/
│   │   ├── product_roadmap.md
│   │   ├── technical_roadmap.md
│   │   └── architecture.md
│   ├── specs/
│   │   └── leadership_button/
│   │       └── spec_[feature_name].md
│   └── project_conventions.md          # This file - documentation standards
├── src/
│   └── leadership_button/
│       └── [feature_name].py
├── tests/
│   ├── test_[feature_name].py
│   └── data/
│       └── [test_subdirectories]/
├── scripts/
│   └── [descriptive_name].py
├── README.md                           # Primary project documentation
└── requirements.txt                    # Python dependencies
```

## 📜 File Naming and Location Conventions

You **MUST** adhere to the following file naming and location conventions for all new files. This "golden thread" connects a feature across the entire project:

- **Specification Files**: Must be placed in `docs/specs/leadership_button/` and named using the format `spec_[feature_name].md`. The directory structure within `docs/specs/` should mirror the `src/` directory.
- **Source Code Files**: Must be placed in `src/leadership_button/` and named `[feature_name].py`, directly corresponding to a spec file.
- **Test Files**: Must be placed in `tests/` and named `test_[feature_name].py`, corresponding to a source file. All meta data for tests will be in `tests/data` categorized within subsequent subdirectories for understanding.
- **Scripts**: Must be placed in `scripts/` and named descriptively (e.g., `deploy_to_pi.py`).

## 📄 Documentation Templates

This section contains the official templates for all project documentation, as defined in the master `.specpilot/spec_driven_prompt.md`.

### Template: `architecture.md`

```markdown
# Project Architecture

## 1. Core Principles

(A list of the fundamental rules that govern the system's design, e.g., security, performance, maintainability.)

## 2. System Overview

(A high-level description of the system's components and how they interact.)

## 3. Component Diagrams

(A series of diagrams using Mermaid.js syntax to visually represent the architecture.)

### 3.1. High-Level Flowchart

(A flowchart showing the main user-to-system interaction.)

### 3.2. Sequence Diagram

(A sequence diagram detailing the API calls and data flow.)

## 4. Approved Architectural Deviations Log

(A table logging any temporary, approved violations of the architectural principles for pragmatic development.)

| Task | Rule Violated | Rationale | Resolution Phase |
| :--- | :------------ | :-------- | :--------------- |
|      |               |           |                  |
```

### Template: `spec_*.md`

```markdown
# Specification: [Feature or Module Name]

## 1. Objective

(A clear, concise goal for this specific module or script.)

## 2. Functional Requirements

### Inputs

(What does the function/class take as input? Be specific about types, formats, and constraints.)

### Outputs/Return Values

(What should it produce? Define the exact format.)

### Core Logic

(A step-by-step description of the process.)

### Error Handling

(How should failures be managed? What specific exceptions should be caught and raised?)

## 3. Non-Functional Requirements

(Dependencies, performance constraints, code style, etc.)

## 4. Examples

### Example Usage

(Provide a code snippet showing how you intend to call the function.)

### Example Data

(Provide a small, representative sample of the input and the expected output.)
```

## 🚀 Bootstrap Environment Setup

### Bootstrap Checklist (`bootstrap_py.md`)

**Purpose**: Provides step-by-step instructions for setting up a new Python project environment with all necessary tools and configurations for spec-driven development.

**Location**: `.specpilot/bootstrap_py.md`

**Function**: The master manual setup checklist that guides developers through:

1. Initial folder and Git setup
2. Cursor AI environment configuration with spec-driven mode
3. Core configuration files creation
4. Python environment and quality tools setup
5. AI Bootstrap process execution

This document serves as the authoritative guide for project initialization, replacing the previous individual `create_*.md` prompt files.

## 🧪 Testing Standards

All tests must follow these strict principles as defined in the master prompt:

**Test Architecture Principles**

1. **No Business Logic in Tests**: Tests should only contain orchestration and verification logic.
2. **Centralized Methods**: Main application files must provide centralized methods that can be orchestrated by test suites.
3. **Thorough Testing**: Tests must be comprehensive and cover all critical paths, edge cases, and error conditions.
4. **No Mocking Without Consent**: Do not mock components without explicit user consent, except for the LLM.
5. **LLM Mocking Exception**: The LLM component may be mocked to bypass AI processing and focus on audio pipeline validation.
6. **Test Isolation**: Each test should be independent.
7. **Clear Test Structure**: Follow a clear Arrange-Act-Assert pattern.
8. **STRICT: No Test Code in Main Files**: Main application files must NEVER contain test-related code.

**CRITICAL ANTI-PATTERNS TO AVOID** 9. **NO MANUAL INPUT TESTS**: Tests must be fully automated and require no human interaction. 10. **NO VERBOSE OUTPUT TESTS**: Tests must not print verbose user-facing instructions. 11. **NO DUPLICATE APPLICATION TESTS**: Tests must not recreate the main application's functionality. 12. **NO TESTING THEATER**: Tests must provide real verification value.

**Test Implementation Requirements**

- **Orchestration**: Tests orchestrate calls to centralized methods in main application files.
- **Verification**: Tests verify outputs, state changes, and side effects.
- **Automated Only**: All tests must run completely without human intervention.
- **Minimal Output**: Tests should have minimal console output (pass/fail only).
- **Single Purpose**: Each test should verify one specific function or behavior.

**Enforcement Rules**

- Before any code change, check if the change adds test-related functionality to main files.
- If in doubt, ask "Is this code needed for the application to function, or only for testing?"
- Violation penalty: Any test code in main files must be immediately removed and moved to test files.

## 🔄 Documentation Lifecycle

1. **Specification First**: All features begin with a spec file in `docs/specs/leadership_button/`
2. **Implementation**: Source code is created in `src/leadership_button/` following the spec
3. **Testing**: Comprehensive tests are created in `tests/` to verify the implementation
4. **Architecture Compliance**: All code must adhere to principles defined in `docs/plans/architecture.md`

## 📝 Content Standards

- **Clarity**: All documentation must be clear, concise, and actionable
- **Completeness**: Specifications must include all necessary details for implementation
- **Consistency**: Use the provided templates for all documentation
- **Traceability**: Maintain clear connections between specs, code, and tests
- **Single Source of Truth**: The `.specpilot/spec_driven_prompt.md` file contains the master templates and protocols

## 🏛️ Sources of Truth Hierarchy

1. **Primary**: `.specpilot/spec_driven_prompt.md` - Master AI operational protocols and templates
2. **Secondary**: `docs/project_conventions.md` - This file, derived from the master prompt
3. **Tertiary**: `docs/plans/architecture.md` - System design principles (when it exists)
4. **Bootstrap**: `.specpilot/bootstrap_py.md` - Environment setup procedures

## 🧹 File Management Rules

**Consolidated Structure**: The multiple `create_*.md` files have been replaced by:

- Templates in `.specpilot/spec_driven_prompt.md`
- Setup procedures in `.specpilot/bootstrap_py.md`

**Redundant Files**: The following files are now obsolete and should be removed:

- `create_product_md_prompt.md`
- `create_product_roadmap_md_prompt.md`
- `create_technical_roadmap_md.md`

**Location Standards**: All AI-related configuration files must be in `.specpilot/`, consolidating workflow logic in a hidden directory.
