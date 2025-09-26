#!/usr/bin/env python3
"""
Simple Alpha Vantage API Test Script
Test your Alpha Vantage API key without requiring the full backend setup
"""

import os
import requests
import json
import time
from datetime import datetime
from dotenv import load_dotenv

def test_alpha_vantage_api():
    """Test Alpha Vantage API functionality"""
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    
    if not api_key or api_key == 'your_alpha_vantage_api_key_here':
        print("❌ Alpha Vantage API key not found!")
        print("Please add your API key to the .env file:")
        print("ALPHA_VANTAGE_API_KEY=your_actual_api_key_here")
        return False
    
    print(f"🔑 Testing Alpha Vantage API with key: {api_key[:8]}...")
    print("=" * 60)
    
    base_url = "https://www.alphavantage.co/query"
    
    def make_request(params):
        """Make API request with rate limiting"""
        params['apikey'] = api_key
        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    try:
        # Test 1: Search Symbols
        print("🔍 Testing Symbol Search...")
        search_data = make_request({
            'function': 'SYMBOL_SEARCH',
            'keywords': 'Apple'
        })
        
        if search_data and 'bestMatches' in search_data:
            matches = search_data['bestMatches']
            print(f"✅ Found {len(matches)} results for 'Apple'")
            for i, match in enumerate(matches[:3]):  # Show first 3
                print(f"   {i+1}. {match['1. symbol']} - {match['2. name']}")
        else:
            print("❌ No search results found")
            if search_data and 'Error Message' in search_data:
                print(f"   Error: {search_data['Error Message']}")
        print()
        
        # Rate limiting - wait 12 seconds (5 requests per minute = 12 seconds between requests)
        print("⏳ Waiting 12 seconds for rate limiting...")
        time.sleep(12)
        
        # Test 2: Current Price
        print("💰 Testing Current Price...")
        price_data = make_request({
            'function': 'GLOBAL_QUOTE',
            'symbol': 'AAPL'
        })
        
        if price_data and 'Global Quote' in price_data:
            quote = price_data['Global Quote']
            print(f"✅ AAPL Current Price: ${quote['05. price']}")
            print(f"   Change: ${quote['09. change']} ({quote['10. change percent']})")
            print(f"   Volume: {int(quote['06. volume']):,}")
            print(f"   High: ${quote['03. high']}")
            print(f"   Low: ${quote['04. low']}")
        else:
            print("❌ Could not fetch current price")
            if price_data and 'Error Message' in price_data:
                print(f"   Error: {price_data['Error Message']}")
        print()
        
        # Rate limiting
        print("⏳ Waiting 12 seconds for rate limiting...")
        time.sleep(12)
        
        # Test 3: Company Overview
        print("🏢 Testing Company Overview...")
        overview_data = make_request({
            'function': 'OVERVIEW',
            'symbol': 'AAPL'
        })
        
        if overview_data and 'Symbol' in overview_data:
            print(f"✅ Company: {overview_data['Name']}")
            print(f"   Symbol: {overview_data['Symbol']}")
            print(f"   Sector: {overview_data['Sector']}")
            print(f"   Industry: {overview_data['Industry']}")
            print(f"   Market Cap: ${overview_data['MarketCapitalization']}")
            print(f"   P/E Ratio: {overview_data['PERatio']}")
            print(f"   Dividend Yield: {overview_data['DividendYield']}")
        else:
            print("❌ Could not fetch company overview")
            if overview_data and 'Error Message' in overview_data:
                print(f"   Error: {overview_data['Error Message']}")
        print()
        
        # Rate limiting
        print("⏳ Waiting 12 seconds for rate limiting...")
        time.sleep(12)
        
        # Test 4: Daily Data (compact)
        print("📈 Testing Daily Data...")
        daily_data = make_request({
            'function': 'TIME_SERIES_DAILY',
            'symbol': 'AAPL',
            'outputsize': 'compact'
        })
        
        if daily_data and 'Time Series (Daily)' in daily_data:
            time_series = daily_data['Time Series (Daily)']
            dates = list(time_series.keys())
            dates.sort()
            print(f"✅ Retrieved {len(time_series)} days of data")
            print(f"   Date range: {dates[0]} to {dates[-1]}")
            latest = time_series[dates[-1]]
            print(f"   Latest close: ${latest['4. close']}")
        else:
            print("❌ Could not fetch daily data")
            if daily_data and 'Error Message' in daily_data:
                print(f"   Error: {daily_data['Error Message']}")
        print()
        
        print("🎉 Alpha Vantage API tests completed!")
        print("=" * 60)
        print("✅ Your Alpha Vantage API key is working correctly!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Alpha Vantage API: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Alpha Vantage API Test Script")
    print("=" * 60)
    print("This script will test your Alpha Vantage API key with a few basic calls.")
    print("Note: Free tier allows 5 requests per minute, so we'll wait between calls.")
    print()
    
    success = test_alpha_vantage_api()
    
    if success:
        print("\n🎯 Next steps:")
        print("   1. Copy env.example to .env: cp env.example .env")
        print("   2. Edit .env and add your API key")
        print("   3. Start your Stockee application: ./start.sh")
        print("   4. Test the trading interface")
    else:
        print("\n❌ Some tests failed. Please check your API key and try again.")
        print("\n🔧 Troubleshooting:")
        print("   1. Verify your API key is correct")
        print("   2. Check if you've exceeded your daily limit (500 requests)")
        print("   3. Ensure you have a stable internet connection")
        print("   4. Try getting a new API key from alphavantage.co")

if __name__ == "__main__":
    main()
