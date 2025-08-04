### ## 📐 Spec Mode Protocol

Focus on implementing code based on a spec. **You do not propose commits in this mode.**

**Step 1: Propose a Design & Verification Plan**
Before writing any code, respond with a detailed plan. This plan MUST include:

- **Implementation Design**: A summary of the proposed solution, classes, and functions.
- **API Integration Strategy**: If any external APIs are used, this plan MUST detail which API and library will be used and the proposed method for handling credentials. You must default to a secure, environment-based method and NEVER propose hardcoding API keys.
- **Your Self-Check Plan**: How you will ensure your work is correct.
- **📋 Human Verification Plan**: A list of specific, step-by-step instructions for me to manually test the code. This should include any necessary commands to run, sample inputs to provide, and the expected output to look for. You must also provide the `echo` command to print these verification steps to the console for me to follow.

After presenting this complete plan, **STOP** and await my approval.

**🚨 CRITICAL ENFORCEMENT: You are FORBIDDEN from writing ANY implementation code, creating ANY files, or making ANY code changes until you receive explicit approval of your design and verification plan. Violation of this rule is a severe protocol breach.**

**Step 2: Iterate on the Plan**
If my response is not approval, you **MUST** first log `[PLAN_ITERATION]` before addressing my feedback.

**Step 3: Implement and Await Verification**
Write code and tests, log `[CODE_PROPOSED]`, then await my verification result.

**Step 4: Log Failure or Finish**
If I confirm success, the task is complete. If I report a failure, you **MUST** first log `[VERIFICATION_FAILED]` and await my next instruction.
