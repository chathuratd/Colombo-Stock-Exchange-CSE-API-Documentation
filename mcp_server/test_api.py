"""
Example: Test CSE API calls directly
This script tests the CSE API integration without needing an MCP client
"""

import asyncio
import json
from main import make_cse_request


async def test_api_calls():
    """Test various CSE API endpoints"""
    
    print("=" * 70)
    print("CSE API Integration Test")
    print("=" * 70)
    
    tests = [
        {
            "name": "Market Status",
            "endpoint": "marketStatus",
            "data": {}
        },
        {
            "name": "ASPI Index Data",
            "endpoint": "aspiData",
            "data": {}
        },
        {
            "name": "Market Summary",
            "endpoint": "marketSummery",
            "data": {}
        },
        {
            "name": "Company Info (LOLC)",
            "endpoint": "companyInfoSummery",
            "data": {"symbol": "LOLC.N0000"}
        },
        {
            "name": "Top Gainers",
            "endpoint": "topGainers",
            "data": {}
        },
    ]
    
    for i, test in enumerate(tests, 1):
        print(f"\n[{i}/{len(tests)}] Testing: {test['name']}")
        print("-" * 70)
        
        try:
            result = await make_cse_request(test['endpoint'], test['data'])
            print(f"✓ Success! Response preview:")
            
            # Pretty print first 500 chars of response
            response_str = json.dumps(result, indent=2, ensure_ascii=False)
            if len(response_str) > 500:
                print(response_str[:500] + "\n... (truncated)")
            else:
                print(response_str)
                
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print("\n" + "=" * 70)
    print("Test complete!")
    print("=" * 70)


if __name__ == "__main__":
    print("\nThis will make live calls to the CSE API...")
    print("Press Ctrl+C to cancel, or wait 3 seconds to continue...\n")
    
    try:
        asyncio.run(asyncio.sleep(3))
        asyncio.run(test_api_calls())
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
