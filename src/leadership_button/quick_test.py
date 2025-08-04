#!/usr/bin/env python3
"""
Quick test script for non-blocking APIManager initialization.

This script tests the timeout behavior and AI-only mode without
requiring a full debug environment.
"""

import os
import sys
import time
from pathlib import Path

# Add project root to Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))


def test_non_blocking_initialization():
    """Test that APIManager initialization doesn't hang."""
    print("🧪 Testing non-blocking APIManager initialization...")

    start_time = time.time()

    try:
        from src.leadership_button.api_client import APIConfig, APIManager

        print("  ✅ Imports successful")

        # Test with Google Cloud disabled
        os.environ["DISABLE_GOOGLE_CLOUD"] = "true"

        config = APIConfig("config/api_config.json")
        print("  ✅ Config loaded")

        api_manager = APIManager(config)
        print("  ✅ APIManager created")

        elapsed = time.time() - start_time
        print(f"  ⏱️  Initialization took {elapsed:.2f} seconds")

        if elapsed > 10:
            print("  ⚠️  WARNING: Initialization took too long")
            return False

        print(f"  📊 API Manager state: {api_manager.state}")

        if api_manager.state.value == "ai_only":
            print("  ✅ AI-only mode working correctly")
            return True
        else:
            print(f"  ❌ Expected ai_only state, got: {api_manager.state}")
            return False

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"  ❌ Error after {elapsed:.2f} seconds: {e}")
        return False
    finally:
        # Clean up environment
        if "DISABLE_GOOGLE_CLOUD" in os.environ:
            del os.environ["DISABLE_GOOGLE_CLOUD"]


def test_timeout_behavior():
    """Test timeout behavior without disabling Google Cloud."""
    print("\n🧪 Testing timeout behavior with missing credentials...")

    start_time = time.time()

    try:
        from src.leadership_button.api_client import APIConfig, APIManager

        # Ensure Google Cloud is not disabled
        if "DISABLE_GOOGLE_CLOUD" in os.environ:
            del os.environ["DISABLE_GOOGLE_CLOUD"]

        # Clear any Google Cloud credentials
        old_creds = None
        if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
            old_creds = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
            del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

        config = APIConfig("config/api_config.json")
        api_manager = APIManager(config)

        elapsed = time.time() - start_time
        print(f"  ⏱️  Initialization took {elapsed:.2f} seconds")

        if elapsed > 15:
            print("  ❌ FAILED: Initialization took too long (likely hanging)")
            return False

        print(f"  📊 API Manager state: {api_manager.state}")

        if api_manager.state.value in ["ai_only", "ready"]:
            print("  ✅ Non-blocking behavior working correctly")
            return True
        else:
            print(f"  ❌ Unexpected state: {api_manager.state}")
            return False

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"  ❌ Error after {elapsed:.2f} seconds: {e}")
        return False
    finally:
        # Restore credentials if they existed
        if old_creds:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = old_creds


def main():
    """Run all quick tests."""
    print("🚀 Quick Test: Non-Blocking APIManager Initialization")
    print("=" * 60)

    test1_passed = test_non_blocking_initialization()
    test2_passed = test_timeout_behavior()

    print("\n" + "=" * 60)
    print("📊 RESULTS:")
    print(f"  Non-blocking init: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"  Timeout behavior:  {'✅ PASS' if test2_passed else '❌ FAIL'}")

    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED - Non-blocking initialization working!")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED - Check implementation")
        return 1


if __name__ == "__main__":
    sys.exit(main())
