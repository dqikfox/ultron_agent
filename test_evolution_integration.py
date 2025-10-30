#!/usr/bin/env python3
"""
ULTRON Evolution Phase 1 - Integration Test
Quick validation that all new endpoints work together
"""

import json
import urllib.request

def test_evolution_integration():
    """Test that all Phase 1 endpoints integrate correctly"""

    print("\n" + "="*80)
    print("ULTRON EVOLUTION - PHASE 1 INTEGRATION TEST")
    print("="*80)

    endpoints = [
        {
            "method": "GET",
            "path": "/api/system/metrics",
            "name": "System Metrics",
            "description": "Real-time system resource monitoring"
        },
        {
            "method": "GET",
            "path": "/api/health/full",
            "name": "Comprehensive Health",
            "description": "System component health status"
        },
        {
            "method": "GET",
            "path": "/api/autonomous/status",
            "name": "Autonomous Status",
            "description": "Autonomous operation mode status"
        }
    ]

    print("\n📋 Endpoint Integration Test\n")

    results = {}
    for endpoint in endpoints:
        try:
            url = f"http://localhost:8080{endpoint['path']}"
            req = urllib.request.Request(url)
            resp = urllib.request.urlopen(req)
            data = json.load(resp)

            results[endpoint['name']] = {
                'status': 'OK',
                'url': endpoint['path'],
                'description': endpoint['description'],
                'response_keys': list(data.keys())
            }

            print(f"✅ {endpoint['name']}")
            print(f"   └─ {endpoint['description']}")
            print(f"   └─ Endpoint: {endpoint['path']}")
            print(f"   └─ Response keys: {', '.join(list(data.keys())[:3])}...")
            print()

        except Exception as e:
            results[endpoint['name']] = {
                'status': 'ERROR',
                'error': str(e)
            }
            print(f"❌ {endpoint['name']}")
            print(f"   └─ Error: {e}\n")

    # Summary
    print("="*80)
    print("INTEGRATION SUMMARY")
    print("="*80)

    passed = sum(1 for r in results.values() if r.get('status') == 'OK')
    total = len(results)

    print(f"\nPassed: {passed}/{total}")
    print(f"Status: {'✅ ALL SYSTEMS OPERATIONAL' if passed == total else '⚠️ Some endpoints failed'}")

    print("\n" + "="*80)
    print("Key Integration Points:")
    print("="*80)
    print("""
1. System Metrics → Used by Health Dashboard
   └─ Provides CPU/Memory/Disk data
   └─ Health endpoint references these values

2. Health Monitoring → Aggregates all component status
   └─ System metrics → health status calculation
   └─ Component availability → overall status

3. Autonomous Integration → Uses health data
   └─ Health status influences autonomous mode
   └─ Can check system before starting operations

4. Console Execution → Optional dependency
   └─ Can execute safe commands to gather more info
   └─ Used by diagnostics or monitoring tools
    """)

    return passed == total

if __name__ == "__main__":
    success = test_evolution_integration()
    exit(0 if success else 1)
