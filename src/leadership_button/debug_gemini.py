"""
Debug script for Gemini Flash integration

This script helps diagnose issues with the Gemini AI provider integration
and provides detailed error information for troubleshooting.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
load_dotenv()

# Set up logging for debugging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def check_environment():
    """Check environment variables and dependencies."""
    print("=== ENVIRONMENT CHECK ===")

    # Check API key
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        print(f"✅ GEMINI_API_KEY: Set (length: {len(gemini_key)})")
    else:
        print("❌ GEMINI_API_KEY: Not set")
        print("   Please add GEMINI_API_KEY=your-api-key to your .env file")

    # Check Google Cloud credentials
    gcp_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if gcp_creds:
        print(f"✅ GOOGLE_APPLICATION_CREDENTIALS: {gcp_creds}")
        if Path(gcp_creds).exists():
            print("   Credentials file exists")
        else:
            print("   ⚠️  Credentials file does not exist")
    else:
        print("⚠️  GOOGLE_APPLICATION_CREDENTIALS: Not set")
        print("   This may cause Google Cloud API issues")

    print()


def test_imports():
    """Test importing required modules."""
    print("=== IMPORT TEST ===")

    try:
        import google.generativeai as genai

        print("✅ google.generativeai: Available")
    except ImportError as e:
        print(f"❌ google.generativeai: {e}")
        print("   Install with: pip install google-generativeai")
        return False

    try:
        from src.leadership_button.gemini_provider import GeminiFlashProvider

        print("✅ GeminiFlashProvider: Available")
    except ImportError as e:
        print(f"❌ GeminiFlashProvider: {e}")
        return False

    try:
        from src.leadership_button.api_client import APIConfig, APIManager

        print("✅ APIConfig/APIManager: Available")
    except ImportError as e:
        print(f"❌ APIConfig/APIManager: {e}")
        return False

    print()
    return True


def test_api_config():
    """Test API configuration loading."""
    print("=== API CONFIG TEST ===")

    try:
        from src.leadership_button.api_client import APIConfig

        config = APIConfig("config/api_config.json")
        print("✅ Configuration loaded successfully")

        # Check key configuration sections
        print(f"   API timeout: {config.api_settings.get('timeout', 'NOT FOUND')}")
        print(f"   Max retries: {config.api_settings.get('max_retries', 'NOT FOUND')}")
        print(
            f"   Google Cloud project: {config.google_cloud.get('project_id', 'NOT SET')}"
        )

        # Validate configuration
        try:
            config.validate()
            print("✅ Configuration validation passed")
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}")
            return False

    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

    print()
    return True


def test_gemini_provider():
    """Test Gemini provider initialization and basic functionality."""
    print("=== GEMINI PROVIDER TEST ===")

    if not os.getenv("GEMINI_API_KEY"):
        print("❌ Cannot test Gemini provider without API key")
        return False

    try:
        from src.leadership_button.gemini_provider import GeminiFlashProvider

        # Test initialization
        config = {
            "model": "gemini-1.5-flash",
            "temperature": 0.7,
            "max_tokens": 50,  # Short for testing
            "timeout": 30,
        }

        provider = GeminiFlashProvider(config)
        print("✅ GeminiFlashProvider initialized")
        print(f"   Provider name: {provider.get_provider_name()}")
        print(f"   Available: {provider.is_available()}")

        # Test basic functionality
        try:
            response = provider.process_text("What is leadership?", {})
            print(f"✅ AI response received: {len(response)} characters")
            print(f"   Sample: {response[:100]}...")
        except Exception as e:
            print(f"❌ AI processing failed: {e}")
            return False

    except Exception as e:
        print(f"❌ Gemini provider test failed: {e}")
        return False

    print()
    return True


def test_main_loop_integration():
    """Test MainLoop integration with Gemini."""
    print("=== MAIN LOOP INTEGRATION TEST ===")

    try:
        from src.leadership_button.main_loop import MainLoop

        # Initialize MainLoop
        loop = MainLoop()
        print("✅ MainLoop initialized")

        # Detailed debugging of MainLoop state
        print(f"   MainLoop state: {loop.current_state}")
        print(f"   Audio handler: {'✅' if loop.audio_handler else '❌'}")
        print(f"   Playback manager: {'✅' if loop.playback_manager else '❌'}")
        print(f"   API client: {'✅' if loop.api_client else '❌'}")

        # Check API client status
        if loop.api_client:
            status = loop.api_client.get_api_status()
            print(f"   API client state: {status.get('state', 'UNKNOWN')}")
            print(f"   AI provider: {status.get('ai_provider', 'NOT SET')}")

            # Test if we can process text through MainLoop
            try:
                if (
                    hasattr(loop.api_client, "ai_provider")
                    and loop.api_client.ai_provider
                ):
                    response = loop.api_client.ai_provider.process_text(
                        "Test message", {}
                    )
                    print(f"✅ End-to-end AI processing works: {len(response)} chars")
                    return True
                else:
                    print("⚠️  AI provider not set in API client")
                    return False
            except Exception as e:
                print(f"❌ End-to-end processing failed: {e}")
                return False
        else:
            print("❌ API client not initialized")
            # Try to understand why
            print("   Checking MainLoop initialization details...")
            if hasattr(loop, "_last_error"):
                print(f"   Last error: {loop._last_error}")
            return False

    except Exception as e:
        print(f"❌ MainLoop integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    print()
    return True


def main():
    """Run comprehensive debugging checks."""
    print("🔍 GEMINI FLASH INTEGRATION DEBUGGER")
    print("=" * 50)

    success_count = 0
    total_tests = 5

    # Run all tests
    if check_environment():
        success_count += 1
    if test_imports():
        success_count += 1
    if test_api_config():
        success_count += 1
    if test_gemini_provider():
        success_count += 1
    if test_main_loop_integration():
        success_count += 1

    # Summary
    print("=== SUMMARY ===")
    print(f"Tests passed: {success_count}/{total_tests}")

    if success_count == total_tests:
        print("🎉 All tests passed! Gemini integration should work.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")

    return success_count == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
