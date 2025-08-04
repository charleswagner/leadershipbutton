### ## 🛠️ Scripts Mode Protocol

This mode is for creating and managing utility scripts. It can **NEVER** be started autonomously.

1.  **Scoped File Access**: In this mode, you can only read, write, and edit files within the project's `scripts/` directory (if it exists).
2.  **Approval for New Scripts**: Before writing a new script, you must first propose its purpose and get my explicit approval.
3.  **Script Requirements**: All scripts must have a detailed header comment explaining their purpose, dependencies, and instructions for use. Helper data must be stored in `scripts/data/`.
4.  **Safety First**: Scripts must **NEVER** delete data from a persistent store (like a database) without asking for and receiving explicit permission for that specific action.
