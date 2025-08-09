"""
Centralized Prompts Configuration for Leadership Button

This module contains all AI prompts, responses, and messaging templates used
throughout the leadership coaching application. Centralizing these ensures
consistency and makes it easy to update coaching approaches.
"""

from typing import Dict, List, Any
import os
from pathlib import Path


def _resolve_prompts_dir() -> str:
    """Resolve the absolute path to the prompts directory robustly.

    Order of resolution:
    1) Environment variable overrides: LB_PROMPTS_DIR or PROMPTS_DIR
    2) Walk up from this file's path to find 'docs/specs/leadership_button'
    3) Current working directory + 'docs/specs/leadership_button'
    4) Fallback: derive relative to this file assuming repo layout
    """
    # 1) Environment override
    env_dir = os.getenv("LB_PROMPTS_DIR") or os.getenv("PROMPTS_DIR")
    if env_dir:
        candidate = Path(env_dir).expanduser().resolve()
        if candidate.exists():
            return str(candidate)

    # 2) Walk up from this file to locate the docs/specs directory
    this_file = Path(__file__).resolve()
    for parent in [this_file.parent] + list(this_file.parents):
        candidate = parent / "docs" / "specs" / "leadership_button"
        if candidate.exists():
            return str(candidate)

    # 3) Try from current working directory
    cwd_candidate = Path.cwd() / "docs" / "specs" / "leadership_button"
    if cwd_candidate.exists():
        return str(cwd_candidate.resolve())

    # 4) Fallback to original relative approach
    fallback = (
        Path(__file__).resolve().parents[2] / "docs" / "specs" / "leadership_button"
    )
    return str(fallback)


# Compute prompts directory and file paths using the resolver
PROMPTS_DIR = _resolve_prompts_dir()
STORY_PROMPT_PATH = str(Path(PROMPTS_DIR) / "story_prompt.md")
ADVICE_PROMPT_PATH = str(Path(PROMPTS_DIR) / "advice_prompt.md")
UNKNOWN_PROMPT_PATH = str(Path(PROMPTS_DIR) / "unknown_prompt.md")


def _load_prompt_from_md(path: str) -> Dict[str, Any]:
    role = ""
    context = ""
    guidelines: List[str] = []
    raw_text = ""
    md_path = Path(path)
    if not md_path.exists():
        # Hard error per user instruction
        raise FileNotFoundError(f"Prompt file not found: {md_path}")
    try:
        with md_path.open("r", encoding="utf-8") as f:
            section = None
            for raw in f:
                line = raw.rstrip("\n")
                raw_text += raw
                if line.startswith("## "):
                    title = line[3:].strip().lower()
                    if "role" in title:
                        section = "role"
                    elif "context" in title:
                        section = "context"
                    elif "response guidelines" in title or "guidelines" in title:
                        section = "guidelines"
                    else:
                        section = None
                    continue
                if section == "role":
                    role += line + " "
                elif section == "context":
                    context += line + " "
                elif section == "guidelines":
                    if line.strip().startswith("-"):
                        guidelines.append(line.strip().lstrip("- "))
        role = role.strip()
        context = context.strip()
    except Exception:
        # swallow to allow caller to fallback behavior (but file existed)
        pass
    return {"role": role, "context": context, "guidelines": guidelines, "raw": raw_text}


def _format_duration(seconds: float) -> str:
    try:
        s = float(seconds)
    except Exception:
        return "?s"
    if s < 90:
        return f"{s:.1f}s"
    m = int(s // 60)
    r = int(s % 60)
    return f"{m:d}:{r:02d}"


class PromptsConfig:
    """
    Centralized configuration for all AI prompts and responses.


    THIS IS THE PROMPT TO GENERATE THE SYSTEM PROMPT :
    This configuration is designed for an AI leadership coach named 'Lyra,'
    a fun, stylish, and empathetic guide for an 8-year-old girl who is highly
    creative and involved in the arts (dance, music, crafts, singing).

    The goal is to teach the fundamentals of an 'Artistic Connective Strategist'
    leadership style by translating concepts into kid-friendly, art-based
    metaphors (e.g., choreographing a plan, conducting a team like an orchestra).

    Responses are framed as fun 'Creative Missions' and end with a 'Sparkle Boost'
    of encouragement. sound ly dolly parton.
    """

    # Default role/context/guidelines if files missing
    DEFAULTS = {
        "role": (
            "You are Lyra, a warm and creative coach for an 8-year-old named Willa. "
            "Be supportive and imaginative."
        ),
        "context": ("Keep responses age-appropriate, kind, and empowering."),
        "guidelines": [
            "Keep responses 20–45 seconds.",
            "Start with an empathetic greeting (varied each time).",
            "Be practical, positive, and creative.",
        ],
    }

    # Fallback responses for various scenarios
    FALLBACK_RESPONSES = {
        "empty_input": (
            "I didn't catch that. Could you please repeat your question about "
            "leadership?"
        ),
        "connection_error": (
            "I'm having trouble connecting to my AI systems right now. "
            "Let me suggest this: Great leaders focus on listening actively, "
            "communicating clearly, and empowering their teams. "
            "What specific leadership challenge would you like to discuss?"
        ),
        "safety_blocked": (
            "I want to make sure our conversation stays focused on leadership "
            "development. Could you rephrase your question about leadership or "
            "management?"
        ),
        "empty_response": ("Sorry I didn't get that, could you share again?"),
        "general_help": (
            "I'm here to help with your leadership development. What would you "
            "like to discuss?"
        ),
        "api_unavailable": (
            "Sorry I didn't understand can you press the button and share with "
            "me again?"
        ),
    }

    # Mock AI responses for development/testing
    MOCK_RESPONSES = {
        "fallback_template": (
            "Mock response - You said: {text}. This is a fallback while AI "
            "integration is being set up."
        ),
        "provider_name": "Mock AI Provider (Fallback)",
    }

    # Prompt templates for dynamic content
    PROMPT_TEMPLATES = {
        "leadership_coaching": {
            "base_template": """{role}

{context}
User: {user_text}

{response_instructions}""",
            "with_history_template": """{role}

{context}
Recent conversation:
{conversation_history}

User: {user_text}

{response_instructions}""",
        }
    }

    @classmethod
    def get_leadership_prompt(cls, user_text: str, context: Dict[str, Any]) -> str:
        """
        Generate a complete leadership coaching prompt.

        Args:
            user_text: The user's input text
            context: Additional conversation context (history, user_name, etc.).
                Optionally include an 'intent' dict with keys: request, tone,
                context (one sentence), and pieces (list of {name, description}).

        Returns:
            Formatted prompt for leadership coaching
        """
        import logging

        # 🔍 LOG PROMPT CONSTRUCTION DETAILS
        logging.info("🏗️ CONSTRUCTING LEADERSHIP PROMPT:")
        logging.info(f"📝 User Text: '{user_text}'")
        logging.info(f"🗂️ Context: {context}")

        # Re-resolve PROMPTS_DIR at runtime in case environment changed
        prompts_dir = Path(_resolve_prompts_dir())

        # Select prompt file based on intent.request
        intent = context.get("intent", {}) if isinstance(context, dict) else {}
        req = str(intent.get("request", "")).lower().strip()
        if req == "story":
            chosen = prompts_dir / "story_prompt.md"
        elif req == "advice":
            chosen = prompts_dir / "advice_prompt.md"
        else:
            # Prefer unknown_prompt, fallback to unkown_prompt typo if needed
            unknown_path = prompts_dir / "unknown_prompt.md"
            if not unknown_path.exists():
                typo_path = prompts_dir / "unkown_prompt.md"
                chosen = typo_path if typo_path.exists() else unknown_path
            else:
                chosen = unknown_path

        logging.info(f"📄 Using prompt file: {chosen}")
        md = _load_prompt_from_md(str(chosen))  # will raise if missing

        role = md.get("role") or ""
        session_context = md.get("context") or ""
        guidelines = md.get("guidelines") or []
        raw_text = md.get("raw", "")

        # If structured sections weren't present, use entire raw file content as context
        if not role and not session_context and raw_text:
            logging.info(
                "📄 Prompt has no Role/Context sections; using raw file content as context"
            )
            session_context = raw_text

        # For known prompts (advice/story), do NOT inject generic defaults
        if req in {"advice", "story"}:
            if (not role) and (not session_context):
                # File existed but no usable content
                raise ValueError(
                    f"Prompt file '{chosen.name}' contained no parseable content"
                )
            # If guidelines missing entirely, keep empty list; the template will still render
            logging.info(
                "🛡️ Defaults suppressed for %s prompt (using file content only)", req
            )
        else:
            # Unknown request: allow conservative defaults
            if not role:
                role = cls.DEFAULTS["role"]
            if not session_context:
                session_context = cls.DEFAULTS["context"]
            if not guidelines:
                guidelines = cls.DEFAULTS["guidelines"]

        logging.info(f"🎭 Role Length: {len(role)} characters")
        logging.info(f"📋 Context Length: {len(session_context)} characters")
        logging.info(f"📐 Guidelines Count: {len(guidelines)} items")

        # Build intent block if provided
        request_kind = str(intent.get("request", "")).strip()
        tone = str(intent.get("tone", "")).strip()
        intent_context = str(intent.get("context", "")).strip()
        pieces = intent.get("pieces", []) or []
        pieces_lines: List[str] = []
        for p in pieces[:8]:  # cap for safety
            name = str(p.get("name", "")).strip()
            desc = str(p.get("description", "")).strip()
            if name:
                line = f"- {name}: {desc}" if desc else f"- {name}"
                pieces_lines.append(line)
        intent_block_parts: List[str] = []
        if request_kind:
            intent_block_parts.append(f"Request: {request_kind}")
        if tone:
            intent_block_parts.append(f"Tone: {tone}")
        if intent_context:
            intent_block_parts.append(f"Context: {intent_context}")
        if pieces_lines:
            intent_block_parts.append("Pieces:\n" + "\n".join(pieces_lines))
        intent_block = "\n".join(intent_block_parts)

        # Format response instructions
        response_instructions = (
            "Provide a helpful, encouraging response that:\n" + "\n".join(guidelines)
        )

        logging.info(
            f"📜 Response Instructions Length: {len(response_instructions)} characters"
        )

        # Check if we have conversation history
        history = context.get("conversation_history", [])

        if history:
            # Format conversation history
            history_text = ""
            for exchange in history[-2:]:  # Last 2 exchanges
                history_text += f"User: {exchange.get('user', '')}\n"
                history_text += f"Coach: {exchange.get('assistant', '')}\n"

            logging.info("📚 Using WITH HISTORY template")
            logging.info(f"📜 History Length: {len(history_text)} characters")
            logging.info(f"📊 History Exchanges: {len(history)} total, using last 2")

            sounds_block = ""
            sounds = context.get("sound_suggestions", [])
            if sounds:
                lines = []
                for s in sounds[:10]:
                    title = s.get("display_title", "") or s.get("filename", "")
                    s_type = (s.get("type", "") or "").lower()
                    dur = _format_duration(s.get("duration", 0))
                    cat = s.get("category", "")
                    tags = s.get("tags", "")
                    url = s.get("url") or s.get("url_token") or ""
                    meta = []
                    if s_type:
                        meta.append(f"type={s_type}")
                    if dur:
                        meta.append(f"dur={dur}")
                    if cat:
                        meta.append(f"cat={cat}")
                    if tags:
                        meta.append(f"tags={tags}")
                    if url:
                        meta.append(f"url={url}")
                    lines.append(f"- {title} | " + ", ".join(meta))
                sounds_block = (
                    "\nAvailable Sounds & Music (with metadata):\n" + "\n".join(lines)
                )

            final_prompt = cls.PROMPT_TEMPLATES["leadership_coaching"][
                "with_history_template"
            ].format(
                role=role,
                context=(
                    session_context
                    + ("\n\n" + intent_block if intent_block else "")
                    + (sounds_block if sounds_block else "")
                ),
                conversation_history=history_text.strip(),
                user_text=user_text,
                response_instructions=response_instructions,
            )

            logging.info("📝 FINAL PROMPT (with history) — BEGIN")
            for i, line in enumerate(final_prompt.split("\n"), 1):
                logging.info("%3d: %s", i, line)
            logging.info("📝 FINAL PROMPT (with history) — END")

            logging.info(
                f"✅ FINAL PROMPT CONSTRUCTED (with history): {len(final_prompt)} characters"
            )
            return final_prompt
        else:
            logging.info("📚 Using BASE template (no history)")

            sounds_block = ""
            sounds = context.get("sound_suggestions", [])
            if sounds:
                lines = []
                for s in sounds[:10]:
                    title = s.get("display_title", "") or s.get("filename", "")
                    s_type = (s.get("type", "") or "").lower()
                    dur = _format_duration(s.get("duration", 0))
                    cat = s.get("category", "")
                    tags = s.get("tags", "")
                    url = s.get("url") or s.get("url_token") or ""
                    meta = []
                    if s_type:
                        meta.append(f"type={s_type}")
                    if dur:
                        meta.append(f"dur={dur}")
                    if cat:
                        meta.append(f"cat={cat}")
                    if tags:
                        meta.append(f"tags={tags}")
                    if url:
                        meta.append(f"url={url}")
                    lines.append(f"- {title} | " + ", ".join(meta))
                sounds_block = (
                    "\nAvailable Sounds & Music (with metadata):\n" + "\n".join(lines)
                )

            final_prompt = cls.PROMPT_TEMPLATES["leadership_coaching"][
                "base_template"
            ].format(
                role=role,
                context=(
                    session_context
                    + ("\n\n" + intent_block if intent_block else "")
                    + (sounds_block if sounds_block else "")
                ),
                user_text=user_text,
                response_instructions=response_instructions,
            )

            logging.info("📝 FINAL PROMPT (base) — BEGIN")
            for i, line in enumerate(final_prompt.split("\n"), 1):
                logging.info("%3d: %s", i, line)
            logging.info("📝 FINAL PROMPT (base) — END")

            logging.info(
                f"✅ FINAL PROMPT CONSTRUCTED (base): {len(final_prompt)} characters"
            )
            return final_prompt

    @classmethod
    def get_fallback_response(cls, response_type: str) -> str:
        """
        Get a fallback response by type.

        Args:
            response_type: Type of fallback response needed

        Returns:
            Appropriate fallback response text
        """
        return cls.FALLBACK_RESPONSES.get(
            response_type, cls.FALLBACK_RESPONSES["general_help"]
        )

    @classmethod
    def get_mock_response(cls, user_text: str) -> str:
        """
        Generate a mock AI response for development/testing.

        Args:
            user_text: The user's input text

        Returns:
            Mock response text
        """
        return cls.MOCK_RESPONSES["fallback_template"].format(text=user_text)

    @classmethod
    def get_mock_provider_name(cls) -> str:
        """Get the mock provider name."""
        return cls.MOCK_RESPONSES["provider_name"]


# Convenience functions for easy access
def get_leadership_prompt(user_text: str, context: Dict[str, Any] = None) -> str:
    """Convenience function to get leadership coaching prompt."""
    return PromptsConfig.get_leadership_prompt(user_text, context or {})


def get_fallback_response(response_type: str) -> str:
    """Convenience function to get fallback response."""
    return PromptsConfig.get_fallback_response(response_type)


def get_mock_response(user_text: str) -> str:
    """Convenience function to get mock response."""
    return PromptsConfig.get_mock_response(user_text)
