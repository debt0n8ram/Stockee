#!/usr/bin/env python3
"""
Comprehensive API Test Script
Test all your API keys: Alpha Vantage, OpenAI, and Polygon.io
"""

import os
import requests
import json
import time
from datetime import datetime
from dotenv import load_dotenv

def test_alpha_vantage():
    """Test Alpha Vantage API"""
    print("🔍 Testing Alpha Vantage API...")
    
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    if not api_key or api_key == 'your_alpha_vantage_api_key_here':
        print("❌ Alpha Vantage API key not configured")
        return False
    
    try:
        # Test current price
        response = requests.get("https://www.alphavantage.co/query", params={
            'function': 'GLOBAL_QUOTE',
            'symbol': 'AAPL',
            'apikey': api_key
        }, timeout=10)
        
        data = response.json()
        if 'Global Quote' in data:
            quote = data['Global Quote']
            print(f"✅ AAPL Price: ${quote['05. price']} ({quote['10. change percent']})")
            return True
        else:
            print(f"❌ Alpha Vantage error: {data.get('Error Message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Alpha Vantage test failed: {e}")
        return False

def test_openai():
    """Test OpenAI API"""
    print("🤖 Testing OpenAI API...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        print("❌ OpenAI API key not configured")
        return False
    
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Test with a simple completion
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [{'role': 'user', 'content': 'Say "Hello from Stockee!"'}],
            'max_tokens': 10
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            print(f"✅ OpenAI Response: {message}")
            return True
        else:
            print(f"❌ OpenAI error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")
        return False

def test_polygon():
    """Test Polygon.io API"""
    print("📊 Testing Polygon.io API...")
    
    api_key = os.getenv('POLYGON_API_KEY')
    if not api_key or api_key == 'your_polygon_api_key_here':
        print("❌ Polygon.io API key not configured")
        return False
    
    try:
        # Test ticker details
        response = requests.get(f"https://api.polygon.io/v3/reference/tickers/AAPL", params={
            'apikey': api_key
        }, timeout=10)
        
        data = response.json()
        if data.get('status') == 'OK' and 'results' in data:
            ticker = data['results']
            print(f"✅ AAPL Details: {ticker['name']} ({ticker['primary_exchange']})")
            return True
        else:
            print(f"❌ Polygon.io error: {data.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Polygon.io test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Stockee API Test Suite")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    results = {}
    
    # Test Alpha Vantage
    results['alpha_vantage'] = test_alpha_vantage()
    print()
    
    # Test OpenAI
    results['openai'] = test_openai()
    print()
    
    # Test Polygon.io
    results['polygon'] = test_polygon()
    print()
    
    # Summary
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for api, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{api.upper()}: {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} APIs working")
    
    if passed_tests == total_tests:
        print("\n🎉 All APIs are working! Your Stockee app is ready to go!")
        print("\n🚀 Next steps:")
        print("   1. Start the application: ./start.sh")
        print("   2. Open http://localhost:3000")
        print("   3. Start trading with real market data!")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} API(s) need attention.")
        print("Check your .env file and API keys.")

if __name__ == "__main__":
    main()
