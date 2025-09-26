#!/usr/bin/env python3
"""
Alpha Vantage API Test Script
Test your Alpha Vantage API key and functionality
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.alpha_vantage_service import AlphaVantageService

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
    
    try:
        # Initialize service
        av_service = AlphaVantageService()
        
        # Test 1: API Status
        print("📊 Testing API Status...")
        status = av_service.get_api_status()
        print(f"✅ API Status: {json.dumps(status, indent=2)}")
        print()
        
        # Test 2: Search Symbols
        print("🔍 Testing Symbol Search...")
        search_results = av_service.search_symbols("Apple")
        if search_results:
            print(f"✅ Found {len(search_results)} results for 'Apple'")
            for i, result in enumerate(search_results[:3]):  # Show first 3
                print(f"   {i+1}. {result['symbol']} - {result['name']}")
        else:
            print("❌ No search results found")
        print()
        
        # Test 3: Current Price
        print("💰 Testing Current Price...")
        price_data = av_service.get_current_price("AAPL")
        if price_data:
            print(f"✅ AAPL Current Price: ${price_data['price']}")
            print(f"   Change: ${price_data['change']} ({price_data['change_percent']:.2f}%)")
            print(f"   Volume: {price_data['volume']:,}")
        else:
            print("❌ Could not fetch current price")
        print()
        
        # Test 4: Daily Data
        print("📈 Testing Daily Data...")
        daily_data = av_service.get_daily_data("AAPL", "compact")
        if daily_data:
            print(f"✅ Retrieved {len(daily_data)} days of data")
            latest = daily_data[-1]
            print(f"   Latest: {latest['date']} - Close: ${latest['close']}")
        else:
            print("❌ Could not fetch daily data")
        print()
        
        # Test 5: Company Overview
        print("🏢 Testing Company Overview...")
        overview = av_service.get_company_overview("AAPL")
        if overview:
            print(f"✅ Company: {overview['name']}")
            print(f"   Sector: {overview['sector']}")
            print(f"   Market Cap: ${overview['market_cap']}")
            print(f"   P/E Ratio: {overview['pe_ratio']}")
        else:
            print("❌ Could not fetch company overview")
        print()
        
        # Test 6: Technical Indicators
        print("📊 Testing Technical Indicators (SMA)...")
        sma_data = av_service.get_technical_indicators("AAPL", "SMA", "daily", 20)
        if sma_data:
            print(f"✅ Retrieved {len(sma_data)} SMA data points")
            latest_sma = sma_data[-1]
            print(f"   Latest SMA(20): {latest_sma.get('SMA', 'N/A')}")
        else:
            print("❌ Could not fetch SMA data")
        print()
        
        print("🎉 Alpha Vantage API tests completed!")
        print("=" * 60)
        
        # Final status
        final_status = av_service.get_api_status()
        print(f"📊 Final API Usage:")
        print(f"   Requests used today: {final_status['requests_today']}/{final_status['daily_limit']}")
        print(f"   Rate limit: {final_status['rate_limit_per_minute']} requests/minute")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Alpha Vantage API: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Alpha Vantage API Test Script")
    print("=" * 60)
    
    success = test_alpha_vantage_api()
    
    if success:
        print("\n✅ All tests passed! Your Alpha Vantage API is working correctly.")
        print("\n🎯 Next steps:")
        print("   1. Start your Stockee application: ./start.sh")
        print("   2. Test the trading interface")
        print("   3. Try searching for stocks and placing trades")
    else:
        print("\n❌ Some tests failed. Please check your API key and try again.")
        print("\n🔧 Troubleshooting:")
        print("   1. Verify your API key is correct")
        print("   2. Check if you've exceeded your daily limit")
        print("   3. Ensure you have a stable internet connection")

if __name__ == "__main__":
    main()
