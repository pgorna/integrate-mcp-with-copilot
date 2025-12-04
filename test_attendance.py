"""
Quick test script to demonstrate the attendance tracking system
"""
import requests
import json
from datetime import date

BASE_URL = "http://localhost:8000"

def test_attendance_system():
    print("🎯 Testing Attendance Tracking System\n")
    
    # 1. Mark attendance for Chess Club
    print("1️⃣ Marking attendance for Chess Club (2024-12-01)")
    attendance_data = {
        "date": "2024-12-01",
        "records": [
            {"email": "michael@mergington.edu", "status": "present"},
            {"email": "daniel@mergington.edu", "status": "absent"}
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/activities/Chess Club/attendance",
        json=attendance_data
    )
    print(f"   Response: {response.json()}\n")
    
    # 2. Mark attendance for another date
    print("2️⃣ Marking attendance for Chess Club (2024-12-04)")
    attendance_data = {
        "date": "2024-12-04",
        "records": [
            {"email": "michael@mergington.edu", "status": "present"},
            {"email": "daniel@mergington.edu", "status": "present"}
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/activities/Chess Club/attendance",
        json=attendance_data
    )
    print(f"   Response: {response.json()}\n")
    
    # 3. Get attendance for specific date
    print("3️⃣ Getting attendance for Chess Club on 2024-12-01")
    response = requests.get(
        f"{BASE_URL}/activities/Chess Club/attendance",
        params={"date": "2024-12-01"}
    )
    print(f"   Response: {json.dumps(response.json(), indent=2)}\n")
    
    # 4. Get all attendance records
    print("4️⃣ Getting all attendance records for Chess Club")
    response = requests.get(f"{BASE_URL}/activities/Chess Club/attendance")
    print(f"   Response: {json.dumps(response.json(), indent=2)}\n")
    
    # 5. Get attendance statistics
    print("5️⃣ Getting attendance statistics for Chess Club")
    response = requests.get(f"{BASE_URL}/activities/Chess Club/attendance/stats")
    print(f"   Response: {json.dumps(response.json(), indent=2)}\n")
    
    # 6. Get student's attendance across all activities
    print("6️⃣ Getting attendance for michael@mergington.edu")
    response = requests.get(f"{BASE_URL}/students/michael@mergington.edu/attendance")
    print(f"   Response: {json.dumps(response.json(), indent=2)}\n")
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    print("Make sure the FastAPI server is running: uvicorn src.app:app --reload")
    print("Then run this test script.\n")
    
    try:
        test_attendance_system()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to server. Make sure it's running!")
    except Exception as e:
        print(f"❌ Error: {e}")
