"""
Gemini Flash AI Provider for Leadership Button

This module implements the AIProvider interface using Google's Gemini Flash model
for AI-powered leadership coaching responses. It follows the project's security
architecture by requiring API keys to be stored in .env files.
"""

import logging
import json
import os
from typing import Dict, Optional, Any
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

# Import the AIProvider interface from api_client
from .api_client import AIProvider
from .prompts_config import PromptsConfig
from .intent_analyzer import IntentAnalyzer

# Gemini AI dependencies
try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning(
        "Google Generative AI library not available - Gemini functionality will be limited"
    )


class GeminiFlashProvider(AIProvider):
    """
    Gemini Flash AI Provider implementation for leadership coaching.

    Implements the AIProvider interface using Google's Gemini Flash model
    optimized for speed and responsiveness in leadership coaching scenarios.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Gemini Flash provider.

        Args:
            config: Optional configuration dictionary for model parameters

        Raises:
            ValueError: If GEMINI_API_KEY not found in environment variables
            RuntimeError: If Gemini library is not available
        """
        if not GEMINI_AVAILABLE:
            raise RuntimeError(
                "Google Generative AI library not installed. "
                "Install with: pip install google-generativeai"
            )

        # Enforce security architecture: API key must be in .env file
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment variables. "
                "Please add GEMINI_API_KEY=your-api-key to your .env file"
            )

        # Configure the Gemini API
        genai.configure(api_key=self.api_key)

        # Set up configuration with defaults
        self.config = config or {}
        self.model_name = self.config.get("model", "gemini-1.5-flash")
        self.temperature = self.config.get("temperature", 0.7)
        self.max_tokens = self.config.get("max_tokens", 150)
        self.timeout = self.config.get("timeout", 30)

        # Initialize the model
        try:
            self.model = genai.GenerativeModel(self.model_name)
            self._is_available = True
            logging.info(
                f"Gemini Flash provider initialized with model: {self.model_name}"
            )
        except Exception as e:
            logging.error(f"Failed to initialize Gemini model: {e}")
            self._is_available = False
            raise RuntimeError(f"Failed to initialize Gemini model: {e}")

        # Intent analyzer
        try:
            self.intent_analyzer = IntentAnalyzer(model=self.model_name)
        except Exception as exc:
            logging.warning("Intent analyzer unavailable: %s", exc)
            self.intent_analyzer = None

        # Safety settings for leadership coaching context
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }

        # Generation configuration
        self.generation_config = genai.types.GenerationConfig(
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
        )

    def process_text(self, text: str, context: Dict[str, Any]) -> str:
        """
        Process text through Gemini Flash and return leadership coaching response.

        Args:
            text: User input text to process
            context: Additional context for the conversation

        Returns:
            AI-generated leadership coaching response

        Raises:
            RuntimeError: If the provider is not available or request fails
        """
        if not self._is_available:
            raise RuntimeError("Gemini Flash provider is not available")

        if not text or not text.strip():
            return PromptsConfig.get_fallback_response("empty_input")

        # 🔍 LOG PROMPT GENERATION DETAILS
        logging.info("=" * 60)
        logging.info("🎯 PROMPT GENERATION STARTED:")
        logging.info("=" * 60)
        logging.info(f"📝 USER INPUT: '{text}'")
        logging.info(f"📏 INPUT LENGTH: {len(text)} characters")
        logging.info(f"🗂️ CONTEXT PROVIDED: {context}")
        logging.info(f"📋 CONTEXT KEYS: {list(context.keys()) if context else 'None'}")

        # Also print to console
        print("\n🎯 GENERATING PROMPT:")
        print(f"📝 User: '{text[:100]}{'...' if len(text) > 100 else ''}'")
        print(f"🗂️ Context: {list(context.keys()) if context else 'None'}")

        # Create leadership coaching prompt using centralized config
        intent = None
        if self.intent_analyzer:
            intent = self.intent_analyzer.analyze(text)
        if intent:
            # Shallow copy to avoid side effects
            context = dict(context or {})
            context["intent"] = intent
            try:
                logging.info(
                    "🧭 Intent Analysis (provider): %s",
                    json.dumps(intent, ensure_ascii=False),
                )
            except Exception:
                logging.info("🧭 Intent Analysis (provider): %s", intent)
        prompt = PromptsConfig.get_leadership_prompt(text, context)

        # 🔍 LOG GENERATED PROMPT DETAILS
        logging.info("✅ PROMPT GENERATED SUCCESSFULLY:")
        logging.info(f"📏 FINAL PROMPT LENGTH: {len(prompt)} characters")
        logging.info(f"🎯 PROMPT PREVIEW: '{prompt[:200]}...'")
        logging.info("=" * 60)
        # Log and print full prompt for debugging
        logging.info("📝 FULL PROMPT — BEGIN")
        for i, line in enumerate(prompt.split("\n"), 1):
            logging.info("%3d: %s", i, line)
        logging.info("📝 FULL PROMPT — END")
        print("\n📝 FULL PROMPT — BEGIN")
        for i, line in enumerate(prompt.split("\n"), 1):
            print(f"{i:3d}: {line}")
        print("📝 FULL PROMPT — END")

        print("✅ Generated prompt: {} characters".format(len(prompt)))

        try:
            # Make the API request with retry logic
            response = self._make_api_request(prompt)

            # Validate and clean the response
            raw_text = response
            # Print and log raw AI response text
            logging.info("📩 AI RAW RESPONSE — BEGIN")
            for i, line in enumerate((raw_text or "").split("\n"), 1):
                logging.info("%3d: %s", i, line)
            logging.info("📩 AI RAW RESPONSE — END")
            print("\n📩 AI RAW RESPONSE — BEGIN")
            for i, line in enumerate((raw_text or "").split("\n"), 1):
                print(f"{i:3d}: {line}")
            print("📩 AI RAW RESPONSE — END")

            cleaned_response = self._clean_response(raw_text)

            logging.info(
                "Successfully processed text with Gemini Flash: %s chars -> %s chars",
                len(text),
                len(cleaned_response),
            )
            return cleaned_response

        except Exception as e:
            logging.error(f"Failed to process text with Gemini Flash: {e}")
            # Use centralized fallback response
            return PromptsConfig.get_fallback_response("connection_error")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    )
    def _make_api_request(self, prompt: str) -> str:
        """
        Make the actual API request to Gemini Flash.

        Args:
            prompt: The complete prompt to send to Gemini

        Returns:
            Raw response text from Gemini

        Raises:
            Exception: If the API request fails
        """

        # 🔍 LOG COMPLETE PROMPT BEING SENT TO GEMINI
        logging.info("=" * 80)
        logging.info("🤖 GEMINI API REQUEST - COMPLETE PROMPT:")
        logging.info("=" * 80)
        logging.info(f"📝 PROMPT LENGTH: {len(prompt)} characters")
        logging.info("📋 FULL PROMPT CONTENT:")
        for i, line in enumerate(prompt.split("\n"), 1):
            logging.info(f"   {i:2d}: {line}")

        # Check if response guidelines are present
        has_empathy = "big dose of empathy" in prompt
        has_missions = "Creative Missions" in prompt
        has_sparkle = "Sparkle Boost" in prompt

        logging.info("🎯 RESPONSE GUIDELINES CHECK:")
        logging.info(f"   ✅ Empathy guideline: {'✓' if has_empathy else '✗'}")
        logging.info(f"   ✅ Creative Missions: {'✓' if has_missions else '✗'}")
        logging.info(f"   ✅ Sparkle Boost: {'✓' if has_sparkle else '✗'}")
        logging.info("=" * 80)

        # Also print to console for immediate visibility
        print("\n🤖 SENDING TO GEMINI:")
        print(
            "📝 Prompt: {} chars | Guidelines: Empathy {} | Missions {} | Sparkle {}".format(
                len(prompt),
                "✓" if has_empathy else "✗",
                "✓" if has_missions else "✗",
                "✓" if has_sparkle else "✗",
            )
        )

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings,
                request_options={"timeout": self.timeout},
            )

            # Check if response was blocked by safety filters
            if response.prompt_feedback.block_reason:
                logging.warning(
                    f"Gemini response blocked: {response.prompt_feedback.block_reason}"
                )
                return PromptsConfig.get_fallback_response("safety_blocked")

            # Extract text from response
            if response.candidates and response.candidates[0].content.parts:
                return response.candidates[0].content.parts[0].text
            else:
                logging.warning("Empty response from Gemini Flash")
                return PromptsConfig.get_fallback_response("empty_response")

        except Exception as e:
            logging.error(f"Gemini API request failed: {e}")
            raise

    def _clean_response(self, response: str) -> str:
        """
        Clean and validate the Gemini response.

        Args:
            response: Raw response from Gemini

        Returns:
            Cleaned response text
        """
        if not response:
            return PromptsConfig.get_fallback_response("empty_response")

        # Remove any potential markdown formatting
        cleaned = response.strip()
        cleaned = cleaned.replace("**", "").replace("*", "")

        # Optional: Limit to 5000 characters if response is extremely long
        if len(cleaned) > 5000:
            logging.info(f"Response truncated from {len(cleaned)} to 5000 characters")
            cleaned = cleaned[:5000]
            # Find a good breaking point to avoid cutting mid-sentence
            last_period = cleaned.rfind(". ")
            if last_period > 4000:  # Only truncate at period if it's not too early
                cleaned = cleaned[: last_period + 1]

        return cleaned

    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "Gemini Flash"

    def is_available(self) -> bool:
        """Check if the provider is available."""
        return self._is_available and GEMINI_AVAILABLE

    def configure(self, settings: Dict[str, Any]) -> None:
        """
        Configure provider settings.

        Args:
            settings: Configuration settings to update
        """
        if "temperature" in settings:
            self.temperature = float(settings["temperature"])
        if "max_tokens" in settings:
            self.max_tokens = int(settings["max_tokens"])
        if "timeout" in settings:
            self.timeout = int(settings["timeout"])

        # Update generation config
        self.generation_config = genai.types.GenerationConfig(
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
        )

        logging.info(
            "Gemini Flash provider configured: temp=%s, max_tokens=%s",
            self.temperature,
            self.max_tokens,
        )

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model configuration.

        Returns:
            Dictionary with model information
        """
        return {
            "provider": "Gemini Flash",
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
            "available": self.is_available(),
        }
