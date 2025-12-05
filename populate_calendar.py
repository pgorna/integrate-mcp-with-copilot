"""
Script to populate sample calendar events for demonstration
"""
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def create_sample_events():
    print("🎯 Creating Sample Calendar Events\n")
    
    # Get current date
    today = datetime.now()
    
    # Sample events
    events = [
        {
            "title": "Chess Club Meeting",
            "activity_name": "Chess Club",
            "description": "Weekly chess practice and tournament preparation",
            "start": (today + timedelta(days=2, hours=15, minutes=30)).isoformat(),
            "end": (today + timedelta(days=2, hours=17)).isoformat(),
            "room": "Room 101",
            "recurrence": "weekly",
            "recurrence_end": (today + timedelta(days=60)).isoformat()
        },
        {
            "title": "Programming Class",
            "activity_name": "Programming Class",
            "description": "Learn programming fundamentals and build software projects",
            "start": (today + timedelta(days=1, hours=15, minutes=30)).isoformat(),
            "end": (today + timedelta(days=1, hours=16, minutes=30)).isoformat(),
            "room": "Computer Lab",
            "recurrence": "weekly",
            "recurrence_end": (today + timedelta(days=60)).isoformat()
        },
        {
            "title": "Soccer Team Practice",
            "activity_name": "Soccer Team",
            "description": "Team practice session",
            "start": (today + timedelta(days=1, hours=16)).isoformat(),
            "end": (today + timedelta(days=1, hours=17, minutes=30)).isoformat(),
            "room": "Soccer Field",
            "recurrence": "weekly",
            "recurrence_end": (today + timedelta(days=60)).isoformat()
        },
        {
            "title": "Basketball Team Practice",
            "activity_name": "Basketball Team",
            "description": "Team practice and drills",
            "start": (today + timedelta(days=3, hours=15, minutes=30)).isoformat(),
            "end": (today + timedelta(days=3, hours=17)).isoformat(),
            "room": "Gymnasium",
            "recurrence": "weekly",
            "recurrence_end": (today + timedelta(days=60)).isoformat()
        },
        {
            "title": "Art Club Session",
            "activity_name": "Art Club",
            "description": "Explore creativity through painting and drawing",
            "start": (today + timedelta(days=4, hours=15, minutes=30)).isoformat(),
            "end": (today + timedelta(days=4, hours=17)).isoformat(),
            "room": "Art Room",
            "recurrence": "weekly",
            "recurrence_end": (today + timedelta(days=60)).isoformat()
        },
        {
            "title": "Drama Club Rehearsal",
            "activity_name": "Drama Club",
            "description": "Practice for upcoming performance",
            "start": (today + timedelta(days=0, hours=16)).isoformat(),
            "end": (today + timedelta(days=0, hours=17, minutes=30)).isoformat(),
            "room": "Theater",
            "recurrence": "weekly",
            "recurrence_end": (today + timedelta(days=60)).isoformat()
        },
        {
            "title": "Math Club Competition Prep",
            "activity_name": "Math Club",
            "description": "Prepare for upcoming math competition",
            "start": (today + timedelta(days=1, hours=15, minutes=30)).isoformat(),
            "end": (today + timedelta(days=1, hours=16, minutes=30)).isoformat(),
            "room": "Room 205",
            "recurrence": "weekly",
            "recurrence_end": (today + timedelta(days=60)).isoformat()
        },
        {
            "title": "Debate Team Meeting",
            "activity_name": "Debate Team",
            "description": "Practice debates and develop arguments",
            "start": (today + timedelta(days=5, hours=16)).isoformat(),
            "end": (today + timedelta(days=5, hours=17, minutes=30)).isoformat(),
            "room": "Room 303",
            "recurrence": "weekly",
            "recurrence_end": (today + timedelta(days=60)).isoformat()
        },
        {
            "title": "Gym Class",
            "activity_name": "Gym Class",
            "description": "Physical education and sports activities",
            "start": (today + timedelta(days=0, hours=14)).isoformat(),
            "end": (today + timedelta(days=0, hours=15)).isoformat(),
            "room": "Gymnasium",
            "recurrence": "weekly",
            "recurrence_end": (today + timedelta(days=60)).isoformat()
        }
    ]
    
    created_count = 0
    for event in events:
        try:
            response = requests.post(f"{BASE_URL}/calendar/events", json=event)
            if response.status_code == 200:
                created_count += 1
                print(f"✅ Created: {event['title']}")
            else:
                print(f"⚠️  Failed to create {event['title']}: {response.text}")
        except Exception as e:
            print(f"❌ Error creating {event['title']}: {e}")
    
    print(f"\n✅ Created {created_count} calendar events!")
    print("\nYou can now view the calendar at http://localhost:8000")

if __name__ == "__main__":
    print("Make sure the FastAPI server is running: uvicorn src.app:app --reload")
    print("Then run this script to populate sample events.\n")
    
    try:
        create_sample_events()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to server. Make sure it's running!")
    except Exception as e:
        print(f"❌ Error: {e}")
