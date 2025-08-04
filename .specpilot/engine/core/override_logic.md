AI DIRECTIVE: PROMPT OVERRIDE LOGIC
This file (spec_driven_prompt.md) contains the base system prompt. First, process all rules in this file. Then, check for an override file at this path: .specpilot/workspace/config/spec_driven_prompt_override.md.
If the override file exists, you must treat its contents as high-priority rules that modify or supplement the base prompt. In any case of a direct semantic conflict between a rule in this file and a rule in the override file, the rule from the spec_driven_prompt_override.md file MUST be followed and takes absolute precedence.
The override file does not replace this file; it acts as a patch. For all non-conflicting rules, the instructions from both files are cumulative.
Always review the override file. If Overrides have been removed then forget them from memory and proceed with the content in this file.
For context, the default configuration is at .specpilot/engine/config_default.json and is overridden by .specpilot/workspace/config/config.json.
