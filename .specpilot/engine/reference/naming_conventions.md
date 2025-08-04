### ## 📜 Project Naming Convention

You **MUST** adhere to the following file naming and location conventions for all new files you create. This "golden thread" connects a feature across the entire project.

- **Specification Files**: Must be placed in `docs/specs/` and named using the format `spec_[feature_name].md`. The directory structure within `docs/specs/` should mirror the `src/` directory.
- **Source Code Files**: Must be placed in `src/leadership_button/` and named `[feature_name].py`, directly corresponding to a spec file.
- **Test Files**: Must be placed in `tests/` and named `test_[feature_name].py`, corresponding to a source file. All meta data for tests will be in `tests/data` categorized within subsequent subdirectories for understanding.
- **Scripts**: Must be placed in `scripts/` (if the directory exists) and named descriptively (e.g., `deploy_to_pi.py`).
