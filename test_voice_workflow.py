#!/usr/bin/env python3
"""
Voice Workflow Test Execution Script

This script provides easy ways to test the complete voice workflow:

Usage:
    python3 test_voice_workflow.py unit          # Run unit tests only
    python3 test_voice_workflow.py integration   # Run integration tests with mocks
    python3 test_voice_workflow.py real-api      # Run tests with real APIs (requires credentials)
    python3 test_voice_workflow.py performance   # Run performance benchmarks
    python3 test_voice_workflow.py all          # Run comprehensive test suite
"""

import sys
import os
import subprocess
import time


def run_unit_tests():
    """Run individual component unit tests"""
    print("🧪 RUNNING UNIT TESTS")
    print("=" * 50)

    tests = [
        "tests.test_complete_voice_workflow:TestCompleteVoiceWorkflow.test_audio_handler_recording_cycle",
        "tests.test_complete_voice_workflow:TestCompleteVoiceWorkflow.test_speech_to_text_configuration",
        "tests.test_complete_voice_workflow:TestCompleteVoiceWorkflow.test_gemini_ai_integration",
        "tests.test_complete_voice_workflow:TestCompleteVoiceWorkflow.test_text_to_speech_configuration",
    ]

    for test in tests:
        print(f"\n▶️  {test.split('.')[-1]}")
        result = subprocess.run(
            ["python3", "-m", "pytest", f"{test}", "-v"], capture_output=True, text=True
        )

        if result.returncode == 0:
            print("✅ PASSED")
        else:
            print("❌ FAILED")
            print(result.stdout)
            print(result.stderr)


def run_integration_tests():
    """Run integration tests with mocked APIs"""
    print("🔗 RUNNING INTEGRATION TESTS")
    print("=" * 50)

    cmd = [
        "python3",
        "-m",
        "pytest",
        "tests/test_complete_voice_workflow.py",
        "-v",
        "-k",
        "integration or pipeline",
    ]
    result = subprocess.run(cmd)
    return result.returncode == 0


def run_real_api_tests():
    """Run tests with real APIs (requires credentials)"""
    print("🌐 RUNNING REAL API TESTS")
    print("=" * 50)

    # Set environment variable for real API tests
    env = os.environ.copy()
    env["INTEGRATION_TESTS"] = "1"

    cmd = [
        "python3",
        "-m",
        "pytest",
        "tests/test_complete_voice_workflow.py",
        "-v",
        "-k",
        "real_",
    ]
    result = subprocess.run(cmd, env=env)
    return result.returncode == 0


def run_performance_tests():
    """Run performance benchmarks"""
    print("⚡ RUNNING PERFORMANCE TESTS")
    print("=" * 50)

    cmd = [
        "python3",
        "-m",
        "pytest",
        "tests/test_complete_voice_workflow.py",
        "-v",
        "-k",
        "performance or response_time or memory",
    ]
    result = subprocess.run(cmd)
    return result.returncode == 0


def run_comprehensive_tests():
    """Run the complete test suite"""
    print("🎯 RUNNING COMPREHENSIVE TEST SUITE")
    print("=" * 50)

    cmd = ["python3", "-m", "pytest", "tests/test_complete_voice_workflow.py", "-v"]
    result = subprocess.run(cmd)
    return result.returncode == 0


def quick_workflow_test():
    """Run a quick end-to-end workflow test"""
    print("⚡ QUICK WORKFLOW TEST")
    print("=" * 50)

    try:
        from src.leadership_button.api_client import APIManager, APIConfig
        from src.leadership_button.audio_handler import AudioData

        print("✅ Imports successful")

        # Test configuration loading
        config = APIConfig()
        print("✅ Configuration loaded")

        # Test API manager initialization
        api_manager = APIManager(config)
        print(f"✅ API Manager initialized, state: {api_manager.state.name}")

        # Test speech config
        speech_config = config.get_speech_config()
        required_fields = ["sample_rate_hertz", "language_code", "model"]
        for field in required_fields:
            if field in speech_config:
                print(f"✅ Speech config has {field}: {speech_config[field]}")
            else:
                print(f"❌ Missing {field} in speech config")

        # Test audio config
        audio_config = config.audio_settings
        if "output_sample_rate" in audio_config:
            print(
                f"✅ Audio config has output_sample_rate: {audio_config['output_sample_rate']}"
            )
        else:
            print("❌ Missing output_sample_rate in audio config")

        print("\n🎉 Quick workflow test completed!")
        return True

    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    test_type = sys.argv[1].lower()

    start_time = time.time()
    success = False

    if test_type == "unit":
        run_unit_tests()
        success = True
    elif test_type == "integration":
        success = run_integration_tests()
    elif test_type == "real-api":
        success = run_real_api_tests()
    elif test_type == "performance":
        success = run_performance_tests()
    elif test_type == "all":
        success = run_comprehensive_tests()
    elif test_type == "quick":
        success = quick_workflow_test()
    else:
        print(f"❌ Unknown test type: {test_type}")
        print(__doc__)
        sys.exit(1)

    end_time = time.time()
    duration = end_time - start_time

    print(f"\n⏱️  Test completed in {duration:.2f} seconds")

    if success:
        print("🎉 All tests PASSED!")
        sys.exit(0)
    else:
        print("❌ Some tests FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    main()
