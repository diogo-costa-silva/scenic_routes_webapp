#!/usr/bin/env python3
"""Test script to process a single road (N222) incrementally"""

import json
from process_roads import init_supabase, process_single_road

# Change this to test different roads
ROADS_FILE = "roads_data_test.json"

def main():
    print("🧪 Testing single road processing...")
    print("=" * 70)
    
    # Initialize
    supabase = init_supabase()
    
    # Load test road
    with open(ROADS_FILE, 'r') as f:
        roads = json.load(f)
    
    print(f"\n📋 Loading {len(roads)} road(s) from {ROADS_FILE}")
    
    # Process first road
    if roads:
        result = process_single_road(roads[0], supabase, skip_existing=False)
        
        if result:
            print("\n✅ TEST PASSED: Road processed successfully!")
        else:
            print("\n❌ TEST FAILED: Road processing failed")
        
        return 0 if result else 1
    else:
        print("❌ No roads to process")
        return 1

if __name__ == "__main__":
    exit(main())
