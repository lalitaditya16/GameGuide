
#!/usr/bin/env python3
"""
🧪 Groq Integration Test Script
==============================

This script tests your Groq API integration with the Gemma2-9B model.
Run this script to verify everything is working correctly before deploying your app.

Usage:
    python test_groq_integration.py
"""

import os
import sys
import time
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment_setup():
    """Test if environment variables are properly set."""
    print("🔧 Testing environment setup...")

    groq_key = os.getenv("GROQ_API_KEY")
    rawg_key = os.getenv("RAWG_API_KEY")

    results = []

    if groq_key:
        print("✅ GROQ_API_KEY found")
        results.append(True)
    else:
        print("❌ GROQ_API_KEY not found in environment")
        print("   Get your free key from: https://console.groq.com/keys")
        results.append(False)

    if rawg_key:
        print("✅ RAWG_API_KEY found")
    else:
        print("⚠️ RAWG_API_KEY not found (required for full app functionality)")
        print("   Get your free key from: https://rawg.io/apidocs")

    return all(results)

def test_package_imports():
    """Test if required packages can be imported."""
    print("\n📦 Testing package imports...")

    packages = [
        ("groq", "Groq"),
        ("langchain_groq", "ChatGroq"),
        ("langchain_core.prompts", "ChatPromptTemplate"),
        ("langchain_core.output_parsers", "StrOutputParser"),
        ("streamlit", "streamlit"),
        ("requests", "requests"),
        ("pandas", "pandas")
    ]

    results = []

    for package_name, import_class in packages:
        try:
            if package_name in ["streamlit", "requests", "pandas"]:
                exec(f"import {package_name}")
                print(f"✅ {package_name} imported successfully")
            else:
                module = __import__(package_name, fromlist=[import_class])
                getattr(module, import_class)
                print(f"✅ {package_name}.{import_class} imported successfully")
            results.append(True)
        except ImportError as e:
            print(f"❌ Failed to import {package_name}: {e}")
            if package_name == "groq":
                print("   Install with: pip install groq")
            elif package_name == "langchain_groq":
                print("   Install with: pip install langchain-groq")
            results.append(False)

    return all(results)

def test_groq_connectivity():
    """Test if Groq API is accessible."""
    print("\n🌐 Testing Groq API connectivity...")

    try:
        from groq import Groq

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        # Test with a simple prompt
        start_time = time.time()
        response = client.chat.completions.create(
            messages=[
                {"role": "user", "content": "Say hello in exactly 3 words"}
            ],
            model="gemma2-9b-it",
            max_tokens=10,
            temperature=0.1
        )
        end_time = time.time()

        response_time = end_time - start_time
        response_content = response.choices[0].message.content

        print(f"✅ Groq API connection successful")
        print(f"   Response: '{response_content}'")
        print(f"   Response time: {response_time:.2f} seconds")

        if response_time < 2.0:
            print("   🚀 Response time is excellent!")
        elif response_time < 5.0:
            print("   ⚡ Response time is good")
        else:
            print("   ⏰ Response time is slower than expected")

        return True

    except Exception as e:
        print(f"❌ Groq API connection failed: {e}")
        return False

def test_langchain_integration():
    """Test LangChain integration with Groq."""
    print("\n🔗 Testing LangChain integration...")

    try:
        from langchain_groq import ChatGroq
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        # Initialize ChatGroq
        llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="gemma2-9b-it",
            temperature=0.1
        )

        # Create a simple chain
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful gaming assistant."),
            ("human", "{input}")
        ])

        chain = prompt | llm | StrOutputParser()

        # Test the chain
        start_time = time.time()
        response = chain.invoke({"input": "What is the most popular game genre?"})
        end_time = time.time()

        response_time = end_time - start_time

        print("✅ LangChain integration successful")
        print(f"   Response: '{response[:100]}...'")
        print(f"   Response time: {response_time:.2f} seconds")

        return True

    except Exception as e:
        print(f"❌ LangChain integration failed: {e}")
        return False

def test_gaming_knowledge():
    """Test AI's gaming knowledge."""
    print("\n🎮 Testing gaming knowledge...")

    try:
        from langchain_groq import ChatGroq

        llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="gemma2-9b-it",
            temperature=0.1
        )

        gaming_questions = [
            "Name 3 popular video game genres",
            "What company makes the PlayStation console?",
            "What does RPG stand for in gaming?"
        ]

        for question in gaming_questions:
            try:
                start_time = time.time()
                response = llm.invoke(f"Answer briefly: {question}")
                end_time = time.time()

                response_time = end_time - start_time
                answer = response.content if hasattr(response, 'content') else str(response)

                print(f"✅ Q: {question}")
                print(f"   A: {answer[:100]}...")
                print(f"   Time: {response_time:.2f}s")

            except Exception as e:
                print(f"❌ Failed to answer: {question} - {e}")
                return False

        return True

    except Exception as e:
        print(f"❌ Gaming knowledge test failed: {e}")
        return False

def performance_benchmark():
    """Run performance benchmark."""
    print("\n⚡ Running performance benchmark...")

    try:
        from langchain_groq import ChatGroq

        llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="gemma2-9b-it",
            temperature=0.1
        )

        # Test multiple requests
        test_prompts = [
            "Recommend a popular video game",
            "What is the best gaming platform?",
            "Explain what makes a game fun",
            "Name a famous game developer",
            "What's trending in gaming?"
        ]

        total_time = 0
        total_tokens = 0

        for i, prompt in enumerate(test_prompts, 1):
            start_time = time.time()
            response = llm.invoke(prompt)
            end_time = time.time()

            response_time = end_time - start_time
            total_time += response_time

            # Estimate tokens (rough approximation)
            response_text = response.content if hasattr(response, 'content') else str(response)
            estimated_tokens = len(response_text.split()) * 1.3  # Rough token estimation
            total_tokens += estimated_tokens

            print(f"   Request {i}/5: {response_time:.2f}s")

        avg_time = total_time / len(test_prompts)
        tokens_per_second = total_tokens / total_time if total_time > 0 else 0

        print(f"\n📊 Performance Results:")
        print(f"   Average response time: {avg_time:.2f} seconds")
        print(f"   Estimated tokens/second: {tokens_per_second:.0f}")

        if tokens_per_second > 500:
            print("   🚀 Excellent performance! (>500 tokens/sec)")
        elif tokens_per_second > 200:
            print("   ⚡ Good performance! (>200 tokens/sec)")
        elif tokens_per_second > 50:
            print("   ✅ Acceptable performance (>50 tokens/sec)")
        else:
            print("   ⏰ Performance could be better")

        return True

    except Exception as e:
        print(f"❌ Performance benchmark failed: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 RAWG Streamlit App with Groq Integration Test")
    print("=" * 50)

    tests = [
        ("Environment Setup", test_environment_setup),
        ("Package Imports", test_package_imports),
        ("Groq Connectivity", test_groq_connectivity),
        ("LangChain Integration", test_langchain_integration),
        ("Gaming Knowledge", test_gaming_knowledge),
        ("Performance Benchmark", performance_benchmark)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1

    print(f"\n🎯 Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Your setup is ready to go!")
        print("\n🚀 Next steps:")
        print("   1. Run: streamlit run app.py")
        print("   2. Visit: http://localhost:8501")
        print("   3. Start exploring games with AI assistance!")
    else:
        print("\n⚠️ Some tests failed. Please address the issues above.")
        print("\n🔧 Common fixes:")
        print("   - Install missing packages: pip install -r requirements.txt")
        print("   - Add API keys to .env file")
        print("   - Check internet connection")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
