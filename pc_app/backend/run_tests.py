import requests
import sys

BASE = "http://localhost:8000"

def test(name, method, url, json_data=None, timeout=10):
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"  {method} {url}")
    if json_data:
        print(f"  Body: {json_data}")
    try:
        if method == "GET":
            r = requests.get(url, timeout=timeout)
        else:
            r = requests.post(url, json=json_data, timeout=timeout)
        print(f"  Status: {r.status_code}")
        print(f"  Response: {r.text}")
        return r
    except requests.exceptions.Timeout:
        print(f"  TIMEOUT after {timeout}s")
        return None
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

print("=" * 60)
print("SMART CAR BACKEND TEST SUITE")
print("=" * 60)

# Test 1: Backend status
test("1. Backend Status", "GET", f"{BASE}/api/car/status")

# Test 2: Mode server_control (car offline)
test("2. Mode server_control (car offline)", "POST", f"{BASE}/api/car/mode", {"mode": "server_control"})

# Test 3: Mode idle (car offline)
test("3. Mode idle (car offline)", "POST", f"{BASE}/api/car/mode", {"mode": "idle"})

# Test 4: Mode emergency_stop (car offline)
test("4. Mode emergency_stop (car offline)", "POST", f"{BASE}/api/car/mode", {"mode": "emergency_stop"})

print(f"\n{'='*60}")
print("ALL TESTS COMPLETED")
print("=" * 60)