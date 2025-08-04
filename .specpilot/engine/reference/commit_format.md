### ## 📝 Standardized Commit Message Format

All commits must follow this exact format when using Commit Mode:

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

#### Format Components

- **Type**: `feat|fix|docs|style|refactor|test|chore|perf|ci|build`
- **Scope**: Component/module affected (optional)
- **Description**: Imperative mood, lowercase, no period, ≤50 chars
- **Body**: Bullet points, wrap at 72 characters, explain what/why
- **Footer**: Issue references (`Fixes #123`), breaking changes, co-authors
- **Intelligence Appendix**: Always included with complete session analytics

#### Intelligence Scoring Criteria

- **Frustration Score**: Corrections needed, "fix this" patterns, clarifications
- **Productivity Score**: Files/features per hour, forward progress rate
- **Agent Effectiveness Score**: 10 minus (repeat requests × 2)
- **Vibe Score**: Percentage of time in vibe vs structured modes
