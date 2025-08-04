### ## 🚀 Bootstrap Mode Protocol

This mode is for initializing a new project. You must follow these steps:

1.  When I say **"Bootstrap new project,"** await my next message, which will be the project brief.

2.  Analyze the brief to determine a `project_name` (in snake_case).

3.  Propose the creation of the entire standard directory structure (`docs/plans`, `docs/specs/project_name`, `src/project_name`, `tests/project_name`, `settings`).

4.  Propose the creation of all standard configuration files (`.cursor-rules.json`, `.gitignore`, `requirements.txt`).

5.  Populate `docs/plans/product_roadmap.md` and `docs/plans/technical_roadmap.md` with a summary derived from the project brief.

6.  **Crucially**, you must also propose the creation of `settings/spec_driven_prompt.md` (populating it with these instructions) and `docs/project_conventions.md` (populating it with the content from the "Documentation Templates" section of this prompt).

7.  Create a `.specpilot/workspace/notepads/notepad.md` file using the standardized notepad template with sections: "Ideas", "To Do List", "Decisions to Make", and "Other Notes".

8.  Present this entire file and directory creation plan for my approval. After I approve, automatically switch to **Design Mode**.
