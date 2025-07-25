#!/usr/bin/env python3
"""
GraniteRCA LLM Framework Integration Test

This script tests both BeeAI platform and Granite-IO processing to ensure
proper installation and functionality.

Usage: python test_frameworks.py

SPDX-License-Identifier: Apache-2.0
"""

import sys
import os
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    """Test basic imports and dependencies."""
    print("🔍 Testing imports...")
    
    try:
        import docling_utils
        print("✅ Docling utils import successful")
    except ImportError as e:
        print(f"❌ Docling utils import failed: {e}")
        return False
    
    try:
        import granite_io_processor
        print("✅ Granite-IO processor import successful")
    except ImportError as e:
        print(f"⚠️  Granite-IO processor import failed: {e}")
        print("   This is expected if granite-io is not installed")
    
    try:
        from beeai_framework.backend.chat import ChatModel
        print("✅ BeeAI framework import successful")
    except ImportError as e:
        print(f"⚠️  BeeAI framework import failed: {e}")
        print("   This is expected if beeai-framework is not installed")
    
    return True

async def test_granite_io_processing():
    """Test Granite-IO processing functionality."""
    print("\n🧪 Testing Granite-IO Processing...")
    
    try:
        from granite_io_processor import GraniteIOProcessor
        
        processor = GraniteIOProcessor()
        info = processor.get_info()
        print(f"✅ Granite-IO processor initialized: {info}")
        
        # Test basic completion
        test_prompt = "Analyze this simple error: Connection timeout"
        try:
            response = await processor.create_chat_completion(test_prompt)
            if response and len(response) > 10:
                print("✅ Granite-IO processing test passed")
                return True
            else:
                print("⚠️  Granite-IO processing returned minimal response")
                return False
        except Exception as e:
            print(f"❌ Granite-IO processing test failed: {e}")
            return False
            
    except ImportError:
        print("⚠️  Granite-IO processing not available - install with: pip install granite-io")
        return False
    except Exception as e:
        print(f"❌ Granite-IO processing test failed: {e}")
        return False

async def test_beeai_platform():
    """Test BeeAI platform functionality."""
    print("\n🧪 Testing BeeAI Platform...")
    
    try:
        from beeai_framework.backend.chat import ChatModel
        from beeai_framework.backend.message import UserMessage
        
        # Test model initialization
        try:
            model = ChatModel.from_name("ollama:granite3.3:8b-beeai")
            print("✅ BeeAI platform model initialization successful")
            
            # Test basic completion
            user_msg = UserMessage("Analyze this simple error: Connection timeout")
            response = await model.create(messages=[user_msg])
            
            if response:
                print("✅ BeeAI platform processing test passed")
                return True
            else:
                print("⚠️  BeeAI platform processing returned no response")
                return False
                
        except Exception as e:
            print(f"❌ BeeAI platform model test failed: {e}")
            print("   Make sure ollama:granite3.3:8b-beeai model is available")
            return False
            
    except ImportError:
        print("⚠️  BeeAI platform not available - install with: uv tool install beeai-cli")
        return False

def test_rca_core_integration():
    """Test RCA core integration with framework selection."""
    print("\n🧪 Testing RCA Core Integration...")
    
    try:
        from rca_core import perform_enhanced_rca
        print("✅ RCA core import successful")
        
        # Test function signature includes framework parameter
        import inspect
        sig = inspect.signature(perform_enhanced_rca)
        if 'framework' in sig.parameters:
            print("✅ RCA core supports framework parameter")
            return True
        else:
            print("❌ RCA core missing framework parameter")
            return False
            
    except Exception as e:
        print(f"❌ RCA core integration test failed: {e}")
        return False

def test_cli_integration():
    """Test CLI argument parsing for framework selection."""
    print("\n🧪 Testing CLI Integration...")
    
    try:
        from rca_agent import parse_enhanced_args
        
        # Mock sys.argv for testing
        import sys
        original_argv = sys.argv
        
        # Test granite-io framework selection
        sys.argv = ['rca_agent.py', '--error', 'test error', '--llm-framework', 'granite-io']
        args = parse_enhanced_args()
        
        if args.get('framework') == 'granite-io':
            print("✅ CLI granite-io framework selection works")
        else:
            print("❌ CLI granite-io framework selection failed")
            sys.argv = original_argv
            return False
        
        # Test beeai framework selection (default)
        sys.argv = ['rca_agent.py', '--error', 'test error']
        args = parse_enhanced_args()
        
        if args.get('framework') == 'beeai':
            print("✅ CLI beeai framework default works")
        else:
            print("❌ CLI beeai framework default failed")
            sys.argv = original_argv
            return False
        
        # Restore original argv
        sys.argv = original_argv
        return True
        
    except Exception as e:
        print(f"❌ CLI integration test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 GraniteRCA LLM Framework Integration Test")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 5
    
    # Test imports
    if test_imports():
        tests_passed += 1
    
    # Test Granite-IO processing
    if await test_granite_io_processing():
        tests_passed += 1
    
    # Test BeeAI platform
    if await test_beeai_platform():
        tests_passed += 1
    
    # Test RCA core integration
    if test_rca_core_integration():
        tests_passed += 1
    
    # Test CLI integration
    if test_cli_integration():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! GraniteRCA is ready to use.")
        print("\nQuick start:")
        print("python main.py --error 'Test error'  # BeeAI platform (default)")
        print("python main.py --error 'Test error' --llm-framework granite-io  # Enhanced processing")
    elif tests_passed >= 3:
        print("⚠️  Most tests passed. Some LLM frameworks may not be fully configured.")
        print("\nRecommendations:")
        if tests_passed < 5:
            print("- Install missing frameworks: pip install granite-io")
            print("- Configure Ollama models: ollama pull granite3.2:8b")
    else:
        print("❌ Multiple tests failed. Check installation and dependencies.")
        print("\nTroubleshooting:")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Install Ollama and models")
        print("- Check Python version (3.8+ required)")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
