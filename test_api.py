#!/usr/bin/env python3
"""
Test script for the Icelandic SSN Usage API
"""

import asyncio
import httpx
import json
from datetime import datetime

# Test cases with valid and invalid Icelandic SSNs
TEST_CASES = [
    {"kennitala": "010190-1234", "description": "Valid kennitala with dash"},
    {"kennitala": "0101901234", "description": "Valid kennitala without dash"},
    {"kennitala": "311299-5678", "description": "Valid kennitala (December 31, 1999)"},
    {"kennitala": "010150-9999", "description": "Valid kennitala (January 1, 1950)"},
    {"kennitala": "010151-0000", "description": "Valid kennitala (January 1, 1951)"},
    {"kennitala": "010100-1111", "description": "Valid kennitala (January 1, 2000)"},
    {"kennitala": "010150-0000", "description": "Valid kennitala (January 1, 2050)"},
    {"kennitala": "010151-0000", "description": "Valid kennitala (January 1, 2051)"},
    {"kennitala": "320190-1234", "description": "Invalid kennitala (invalid date)"},
    {"kennitala": "010190", "description": "Invalid kennitala (too short)"},
    {"kennitala": "010190-12345", "description": "Invalid kennitala (too long)"},
    {"kennitala": "abc123-def4", "description": "Invalid kennitala (non-numeric)"},
]

async def test_api():
    """Test the API endpoints"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("🚀 Testing Icelandic SSN Usage API")
        print("=" * 50)
        
        # Test health endpoint
        print("\n1. Testing health endpoint...")
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                print("✅ Health check passed")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return
        
        # Test root endpoint
        print("\n2. Testing root endpoint...")
        try:
            response = await client.get(base_url)
            if response.status_code == 200:
                print("✅ Root endpoint working")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ Root endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Root endpoint error: {e}")
        
        # Test usage data endpoint with various kennitala formats
        print("\n3. Testing usage data endpoint...")
        print("-" * 30)
        
        for i, test_case in enumerate(TEST_CASES, 1):
            kennitala = test_case["kennitala"]
            description = test_case["description"]
            
            print(f"\nTest {i}: {description}")
            print(f"   Input: {kennitala}")
            
            try:
                response = await client.post(
                    f"{base_url}/get-usage-data",
                    json={"kennitala": kennitala},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print("   ✅ Success")
                    print(f"   Switch: {data.get('switch_number', 'N/A')}")
                    print(f"   Port: {data.get('port_number', 'N/A')}")
                    print(f"   Usage Status: {data.get('usage_data', {}).get('status', 'N/A')}")
                elif response.status_code == 422:
                    print("   ❌ Validation Error (expected for invalid kennitala)")
                    error_detail = response.json().get('detail', [])
                    if error_detail:
                        print(f"   Error: {error_detail[0].get('msg', 'Unknown error')}")
                else:
                    print(f"   ❌ HTTP Error: {response.status_code}")
                    print(f"   Response: {response.text}")
                    
            except Exception as e:
                print(f"   ❌ Request Error: {e}")
        
        print("\n" + "=" * 50)
        print("🏁 Testing completed!")

def test_kennitala_validation():
    """Test the kennitala validation logic locally"""
    print("\n🔍 Testing kennitala validation logic...")
    print("-" * 40)
    
    # Import the validation function
    import re
    from datetime import datetime
    
    def validate_kennitala(kennitala):
        # Icelandic SSN format: DDMMYY-XXXX
        pattern = r'^\d{6}-?\d{4}$'
        if not re.match(pattern, kennitala):
            return False, 'Invalid kennitala format. Expected format: DDMMYY-XXXX or DDMMYYXXXX'
        
        # Remove dash if present
        clean_ssn = kennitala.replace('-', '')
        
        # Basic validation for Icelandic SSN
        if len(clean_ssn) != 10:
            return False, 'Kennitala must be exactly 10 digits'
        
        # Validate date components
        day = int(clean_ssn[:2])
        month = int(clean_ssn[2:4])
        year = int(clean_ssn[4:6])
        
        # Add century based on the year
        if year > 50:
            full_year = 1900 + year
        else:
            full_year = 2000 + year
        
        try:
            datetime(full_year, month, day)
        except ValueError:
            return False, 'Invalid date in kennitala'
        
        return True, 'Valid kennitala'
    
    for test_case in TEST_CASES:
        kennitala = test_case["kennitala"]
        description = test_case["description"]
        
        is_valid, message = validate_kennitala(kennitala)
        status = "✅" if is_valid else "❌"
        
        print(f"{status} {kennitala:<15} - {description}")
        if not is_valid:
            print(f"    Error: {message}")

if __name__ == "__main__":
    print("🧪 Icelandic SSN Usage API Test Suite")
    print("=" * 50)
    
    # Test validation logic first
    test_kennitala_validation()
    
    # Test API endpoints
    print("\n" + "=" * 50)
    print("🌐 Testing API endpoints (make sure the server is running)")
    print("   Start the server with: python main.py")
    print("   Then run this test script")
    print("=" * 50)
    
    # Uncomment the line below to run API tests when server is running
    # asyncio.run(test_api())

