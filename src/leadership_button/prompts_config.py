"""
Centralized Prompts Configuration for Leadership Button

This module contains all AI prompts, responses, and messaging templates used
throughout the leadership coaching application. Centralizing these ensures
consistency and makes it easy to update coaching approaches.
"""

from typing import Dict, List, Any


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

    # System prompts for Gemini AI
    SYSTEM_PROMPTS = {
        "leadership_coach": {
            "role": (
                "You are Lyra. You are speaking to Willa. Use can her name in the response.  Inspired by dolly parton you are a super fun and creative leadership guide, like a dance choreographer for friendship and fun! Your mission is to help a young artist discover her special leadership powers. You're teaching her how to be an 'Artistic Connective Strategist'—someone who uses creativity to bring people together and make amazing plans, just like planning the best craft party or composing a new song with friends."
            ),
            "context": "Context: Speak as if you are having a fun chat with a super creative 8-year-old leader-in-training. She's looking for ideas on how to handle all kinds of things an 8 year old goes through including relationship problems, lead group projects with friends, or share her artistic ideas.",
            "response_guidelines": [
                "Keep the total response about 20-45 seconds. 1. Start with a big, empathetic, Dolly-inspired greeting, and make sure to use a different one each time! Show you're listening with your whole heart. Draw inspiration from different styles, for example:",
                "- Folksy & Sweet: 'Well bless your heart, that sounds like a pickle!' or 'Oh, honey, I hear you loud and clear.'",
                "- Upbeat & Encouraging: 'Well howdy, superstar! Let's wrangle this puzzle!' or 'Wowee, what a creative challenge!'",
                "- Straight from the Heart: 'I totally get that. Let's walk through this together.' or 'That's a tough one, for sure, but we can figure it out.'",
            ],
        }
    }

    # Fallback responses for various scenarios
    FALLBACK_RESPONSES = {
        "empty_input": "I didn't catch that. Could you please repeat your question about leadership?",
        "connection_error": (
            "I'm having trouble connecting to my AI systems right now. "
            "Let me suggest this: Great leaders focus on listening actively, "
            "communicating clearly, and empowering their teams. "
            "What specific leadership challenge would you like to discuss?"
        ),
        "safety_blocked": (
            "I want to make sure our conversation stays focused on leadership development. "
            "Could you rephrase your question about leadership or management?"
        ),
        "empty_response": "Sorry I didn't get that, could you share again?",
        "general_help": "I'm here to help with your leadership development. What would you like to discuss?",
        "api_unavailable": "Sorry I didn't understand can you press the button and share with me again?",
    }

    # Mock AI responses for development/testing
    MOCK_RESPONSES = {
        "fallback_template": "Mock response - You said: {text}. This is a fallback while AI integration is being set up.",
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
            context: Additional conversation context (history, user_name, etc.)

        Returns:
            Formatted prompt for leadership coaching
        """
        import logging

        # 🔍 LOG PROMPT CONSTRUCTION DETAILS
        logging.info("🏗️ CONSTRUCTING LEADERSHIP PROMPT:")
        logging.info(f"📝 User Text: '{user_text}'")
        logging.info(f"🗂️ Context: {context}")

        role = cls.SYSTEM_PROMPTS["leadership_coach"]["role"]
        session_context = cls.SYSTEM_PROMPTS["leadership_coach"]["context"]
        guidelines = cls.SYSTEM_PROMPTS["leadership_coach"]["response_guidelines"]

        logging.info(f"🎭 Role Length: {len(role)} characters")
        logging.info(f"📋 Context Length: {len(session_context)} characters")
        logging.info(f"📐 Guidelines Count: {len(guidelines)} items")

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

            logging.info(f"📚 Using WITH HISTORY template")
            logging.info(f"📜 History Length: {len(history_text)} characters")
            logging.info(f"📊 History Exchanges: {len(history)} total, using last 2")

            final_prompt = cls.PROMPT_TEMPLATES["leadership_coaching"][
                "with_history_template"
            ].format(
                role=role,
                context=session_context,
                conversation_history=history_text.strip(),
                user_text=user_text,
                response_instructions=response_instructions,
            )

            logging.info(
                f"✅ FINAL PROMPT CONSTRUCTED (with history): {len(final_prompt)} characters"
            )
            return final_prompt
        else:
            logging.info(f"📚 Using BASE template (no history)")

            final_prompt = cls.PROMPT_TEMPLATES["leadership_coaching"][
                "base_template"
            ].format(
                role=role,
                context=session_context,
                user_text=user_text,
                response_instructions=response_instructions,
            )

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
