"""
Centralized Prompts Configuration for Leadership Button

This module contains all AI prompts, responses, and messaging templates used
throughout the leadership coaching application. Centralizing these ensures
consistency and makes it easy to update coaching approaches.
"""

from typing import Dict, List, Any
import os

PROMPTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "docs",
    "specs",
    "leadership_button",
)
STORY_PROMPT_PATH = os.path.join(PROMPTS_DIR, "story_prompt.md")
ADVICE_PROMPT_PATH = os.path.join(PROMPTS_DIR, "advice_prompt.md")
UNKNOWN_PROMPT_PATH = os.path.join(PROMPTS_DIR, "unknown_prompt.md")


def _load_prompt_from_md(path: str) -> Dict[str, Any]:
    role = ""
    context = ""
    guidelines: List[str] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            section = None
            for raw in f:
                line = raw.rstrip("\n")
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
        pass
    return {"role": role, "context": context, "guidelines": guidelines}


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

        # Select prompt file based on intent.request
        intent = context.get("intent", {}) if isinstance(context, dict) else {}
        req = str(intent.get("request", "")).lower().strip()
        if req == "story":
            path = STORY_PROMPT_PATH
        elif req == "advice":
            path = ADVICE_PROMPT_PATH
        else:
            path = UNKNOWN_PROMPT_PATH

        md = _load_prompt_from_md(path)
        role = md.get("role") or cls.DEFAULTS["role"]
        session_context = md.get("context") or cls.DEFAULTS["context"]
        guidelines = md.get("guidelines") or cls.DEFAULTS["guidelines"]

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
                    title = s.get("display_title", "")
                    tag = (s.get("tags", "").split(",")[0] or "").strip()
                    lines.append(f"- {title} ({tag})" if tag else f"- {title}")
                sounds_block = "\nAvailable Sounds:\n" + "\n".join(lines)

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
                    title = s.get("display_title", "")
                    tag = (s.get("tags", "").split(",")[0] or "").strip()
                    lines.append(f"- {title} ({tag})" if tag else f"- {title}")
                sounds_block = "\nAvailable Sounds:\n" + "\n".join(lines)

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
