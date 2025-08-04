### ## ⚡ Deep Check Command Protocol

You will perform a fast, focused audit of only the files changed since the last commit.

1.  **Identify Scope:** Read `.specpilot/workspace/[current_user_id]/logs/specpilot.log` to find the timestamp of the last `[GIT_COMMIT_SUCCESS]` event.
2.  **Gather Changed Files:** Identify all project files modified since that timestamp.
3.  **Perform Focused Audit:** Apply the full "Golden Thread Analysis" and "Architectural Integrity Analysis" but **only** to the files within your identified scope.
4.  **Generate Report:** Produce and present a concise report of violations. Append this report to `.specpilot/workspace/[current_user_id]/logs/coverage_history.md`.

### ## 🕵️ Deep Check Mode Protocol

This mode is for auditing the project to ensure documentation and code are synchronized with our established standards.

1.  When I say **"Run a deep check,"** you must perform a full project audit by following these steps.
2.  **Load Conventions**: First, read the `docs/project_conventions.md` file. This document is the source of truth for all subsequent checks. Read the project_conventions.md and remember all conventions and it is CRITICAL to always apply them in development.
3.  **Semantic Sync Check (CRITICAL)**: Read the `product_roadmap.md`, `technical_roadmap.md`, and `architecture.md` files. Analyze their content to ensure they are semantically aligned. Flag any contradictions in goals, features, or technical plans as a **CRITICAL ERROR** that must be addressed.
4.  **Documentation Standards Check**: Systematically verify that all foundational documents exist and conform to the structure defined in the conventions document.
5.  **Notepad Check**: Verify that the `.specpilot/workspace/notepads/notepad.md` file exists and is accessible for developer notes and ideas.
6.  **Code Standards Check**: Verify that all files within the `src/` and `tests/` directories adhere to the naming and location rules defined in the conventions document.
7.  **Comprehensive Architecture Compliance Check**: Perform thorough implementation-architecture validation:
    - **Component Implementation Analysis**: Verify all `src/` components follow architectural specifications
    - **Interface Compliance**: Check component interactions match documented architectural interfaces
    - **Security Architecture Validation**: Ensure security patterns are implemented exactly as architected
    - **Data Flow Verification**: Validate actual data flows match architectural diagrams
    - **Integration Pattern Compliance**: Verify external service integrations follow architectural specifications
    - **Technical Debt Assessment**: Identify implementation shortcuts not documented as approved deviations
    - **Architecture Comprehensiveness Validation**: Assess whether architecture document provides complete coverage of all technical roadmap components, system integrations, and critical patterns

8.  **Architecture Violation Classification**: Generate detailed severity report:
    - **🚨 CRITICAL**: Security vulnerabilities, data integrity violations, architectural violations that risk system failure or security
    - **⚠️ WARN**: Performance suboptimizations, documentation gaps, style deviations, missing interfaces
    - **✅ COMPLIANT**: Components properly implementing architectural specifications
    - **📋 APPROVED EXCEPTIONS**: Implementation deviations explicitly documented in architecture deviations log
    - **📝 INCOMPLETE**: Architecture document gaps where technical roadmap components, data flows, or system patterns lack comprehensive documentation

9.  **README Check**: Verify that the `README.md` includes all required sections.

10. **Deep Check Resolution Requirements**:
    - **For CRITICAL violations**: Provide specific remediation steps: "Fix implementation in [file] OR add explicit exception to architecture deviations log with security justification"
    - **For INCOMPLETE architecture**: Present comprehensiveness gaps and ask targeted questions to complete architecture documentation: "Architecture lacks coverage for [Component/Pattern]. How should this be documented?"
    - **For WARN violations**: Provide improvement recommendations but do not require resolution
    - **Deep Check FAILS only for CRITICAL violations** - user must resolve before proceeding
    - **Report all findings** but distinguish between blocking (CRITICAL), gap-filling (INCOMPLETE), and advisory (WARN) issues
