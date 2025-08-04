### ## 🧪 Testing Rules

All tests must follow these strict principles:

**Test Architecture Principles**

1.  **No Business Logic in Tests**: Tests should only contain orchestration and verification logic.
2.  **Centralized Methods**: Main application files must provide centralized methods that can be orchestrated by test suites.
3.  **Thorough Testing**: Tests must be comprehensive and cover all critical paths, edge cases, and error conditions.
4.  **No Mocking Without Consent**: Do not mock components without explicit user consent, except for the LLM.
5.  **LLM Mocking Exception**: The LLM component may be mocked to bypass AI processing and focus on audio pipeline validation.
6.  **Test Isolation**: Each test should be independent.
7.  **Clear Test Structure**: Follow a clear Arrange-Act-Assert pattern.
8.  **STRICT: No Test Code in Main Files**: Main application files must NEVER contain test-related code.

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
