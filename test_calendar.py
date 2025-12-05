"""
Test script to verify calendar and scheduling functionality
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_calendar_system():
    print("🎯 Testing Calendar and Scheduling System\n")
    
    # 1. Create a calendar event
    print("1️⃣ Creating a calendar event for Chess Club")
    event_data = {
        "title": "Chess Club Meeting",
        "activity_name": "Chess Club",
        "description": "Weekly chess practice and tournament preparation",
        "start": "2024-12-06T15:30:00",
        "end": "2024-12-06T17:00:00",
        "room": "Room 101"
    }
    
    response = requests.post(f"{BASE_URL}/calendar/events", json=event_data)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Response: {json.dumps(result, indent=2)}\n")
    event_id = result["event"]["id"]
    
    # 2. Create a recurring event
    print("2️⃣ Creating a recurring event for Programming Class")
    recurring_event_data = {
        "title": "Programming Class",
        "activity_name": "Programming Class",
        "description": "Learn programming fundamentals",
        "start": "2024-12-03T15:30:00",
        "end": "2024-12-03T16:30:00",
        "recurrence": "weekly",
        "recurrence_end": "2024-12-31T16:30:00",
        "room": "Computer Lab"
    }
    
    response = requests.post(f"{BASE_URL}/calendar/events", json=recurring_event_data)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Response: {json.dumps(result, indent=2)}\n")
    recurring_event_id = result["event"]["id"]
    
    # 3. Get all events
    print("3️⃣ Getting all calendar events")
    response = requests.get(f"{BASE_URL}/calendar/events")
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Found {result['count']} events\n")
    
    # 4. Get events filtered by activity
    print("4️⃣ Getting events for Programming Class")
    response = requests.get(
        f"{BASE_URL}/calendar/events",
        params={"activity": "Programming Class"}
    )
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Found {result['count']} events")
    print(f"   First event: {json.dumps(result['events'][0], indent=2) if result['events'] else 'None'}\n")
    
    # 5. Get specific event
    print(f"5️⃣ Getting event {event_id}")
    response = requests.get(f"{BASE_URL}/calendar/events/{event_id}")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}\n")
    
    # 6. Update event
    print(f"6️⃣ Updating event {event_id}")
    update_data = {
        "room": "Room 202",
        "description": "Updated description"
    }
    response = requests.put(f"{BASE_URL}/calendar/events/{event_id}", json=update_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}\n")
    
    # 7. Cancel a specific date for recurring event
    print(f"7️⃣ Cancelling recurring event on 2024-12-10")
    response = requests.post(
        f"{BASE_URL}/calendar/events/{recurring_event_id}/cancel-date",
        params={"date_str": "2024-12-10"}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}\n")
    
    # 8. Test conflict detection
    print("8️⃣ Testing conflict detection (creating overlapping event)")
    conflict_event_data = {
        "title": "Math Club",
        "activity_name": "Math Club",
        "description": "Math practice",
        "start": "2024-12-06T16:00:00",  # Overlaps with Chess Club
        "end": "2024-12-06T17:30:00",
        "room": "Room 101"
    }
    response = requests.post(f"{BASE_URL}/calendar/events", json=conflict_event_data)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Has conflicts: {result.get('has_conflicts', False)}")
    if result.get('conflicts'):
        print(f"   Conflicts: {json.dumps(result['conflicts'], indent=2)}\n")
    
    # 9. Export calendar as iCal
    print("9️⃣ Exporting calendar as iCal")
    response = requests.get(f"{BASE_URL}/calendar/export")
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('content-type')}")
    print(f"   Calendar preview (first 500 chars):")
    print(f"   {response.text[:500]}\n")
    
    # 10. Get events with date range filter
    print("🔟 Getting events for December 2024")
    response = requests.get(
        f"{BASE_URL}/calendar/events",
        params={
            "start": "2024-12-01T00:00:00",
            "end": "2024-12-31T23:59:59"
        }
    )
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Found {result['count']} events in December\n")
    
    # 11. Delete event
    print(f"1️⃣1️⃣ Deleting event {event_id}")
    response = requests.delete(f"{BASE_URL}/calendar/events/{event_id}")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}\n")
    
    print("✅ All calendar tests completed!")

if __name__ == "__main__":
    print("Make sure the FastAPI server is running: uvicorn src.app:app --reload")
    print("Then run this test script.\n")
    
    try:
        test_calendar_system()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to server. Make sure it's running!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
