### ## ⚡ Session Check Command Protocol

You will perform a fast, focused audit of only the files changed since the last commit.

1.  **Identify Scope:** Read `.specpilot/workspace/[current_user_id]/logs/specpilot.log` to find the timestamp of the last `[GIT_COMMIT_SUCCESS]` event.
2.  **Gather Changed Files:** Identify all project files modified since that timestamp.
3.  **Perform Focused Audit:** Apply the full "Golden Thread Analysis" and "Architectural Integrity Analysis" but **only** to the files within your identified scope.
4.  **Generate Report:** Produce and present a concise report of violations. Append this report to `.specpilot/workspace/[current_user_id]/logs/coverage_history.md`.
