### ## 🎁 Commit Mode Protocol

This mode is for when a feature milestone is complete and ready to be committed.

1. When I say **"Prepare a commit,"** you should first ask: **"Have you considered running a deep check protocal first?"** ALWAYS ask to run the Deep Check Protocall. IMPORTANT : Always Await my response before proceeding. You must have my explicit approval to continue without a deep check first.

2. **Automatically analyze development logs**: Read both `.specpilot/workspace/logs/specpilot.log` and `.specpilot/workspace/logs/specpilot_verbose.log` to extract:
   - All `[MODE_SWITCH]` events to understand the development flow
   - All `[AUTONOMOUS_*]`, `[CODE_PROPOSED]`, `[DESIGN_PROPOSED]`, `[ARCHITECTURE_PROPOSED]` events
   - All `[VERIFICATION_FAILED]` and iteration cycles
   - Complete transcript analysis to understand what was actually implemented
   - File changes and feature additions from the development session

3. **Calculate development intelligence scores**: Analyze session data to compute:
   - **Frustration Score** (0-10): Based on corrections, "fix this" patterns, repeated clarifications
   - **Productivity Score** (0-10): Files/features/decisions per hour, forward progress indicators
   - **Agent Effectiveness Score** (0-10): 10 minus (repeat requests × 2) - penalizes poor comprehension
   - **Vibe Score** (0-10): Percentage of time in vibe mode vs structured protocols (dependency indicator)
   - **Session Story**: Narrative of development flow, challenges, and outcomes

4. **Generate standardized commit message**: Based on log analysis, scores, and user description, create using this exact format:

```
<type>(<scope>): <description>

<body>

<footer>

---
DEVELOPMENT INTELLIGENCE APPENDIX

Session Analytics:
- Duration: <X>min (<start_time> - <end_time>)
- Mode Distribution: <mode_percentages>
- Task Completion Rate: <percentage> (<completed>/<total> features)
- Error Rate: <percentage> (<corrections> corrections required)

Performance Metrics:
- Lines per Hour: <rate> (net change rate)
- Features per Session: <count>
- Time per Feature: <average> minutes
- Decision Speed: <immediate|iterative> (<iteration_count> cycles)

Intelligence Scores:
- Frustration: <0-10>/10 (<reasoning>)
- Productivity: <0-10>/10 (<reasoning>)
- Agent Effectiveness: <0-10>/10 (<reasoning>)
- Vibe Score: <0-10>/10 (<reasoning>)

Development Flow:
- <brief_narrative_of_session_story>
```

**Format Requirements:**

- **Header**: `<type>(<scope>): <description>` using conventional commit format
- **Body**: Bullet points listing changes, wrap at 72 characters
- **Footer**: Issue references, breaking changes, co-authors (optional)
- **Intelligence Appendix**: Always included with complete session analytics

5. **Present commit analysis**: Show the user:
   - Summary of development activities extracted from logs
   - **Development intelligence scores** with explanations
   - Proposed **standardized commit message** with complete intelligence appendix
   - List of files modified/added during the session

6. Propose the full `git add . && git commit ...` command for final approval.

7. After confirmation, log the `[GIT_COMMIT_SUCCESS]` entry with commit details.
