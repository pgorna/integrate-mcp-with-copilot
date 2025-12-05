"""
Test script to verify Manga Maniacs activity is properly configured
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_manga_maniacs_exists():
    """Test that Manga Maniacs activity exists in the system"""
    print("🎯 Testing Manga Maniacs Activity\n")
    
    # Get all activities
    print("1️⃣ Fetching all activities...")
    response = requests.get(f"{BASE_URL}/activities")
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch activities: {response.status_code}")
        return False
    
    activities = response.json()
    
    # Check if Manga Maniacs exists
    if "Manga Maniacs" not in activities:
        print("❌ Manga Maniacs activity not found!")
        return False
    
    print("✅ Manga Maniacs activity found!\n")
    
    # Verify the activity details
    manga_maniacs = activities["Manga Maniacs"]
    
    print("2️⃣ Verifying activity details...")
    
    # Check description
    expected_description = "Dive into the epic worlds of Japanese Manga! Discover legendary heroes, intense battles, heartwarming friendships, and mind-bending plot twists. From shonen adventures to slice-of-life stories, unleash your inner otaku!"
    if manga_maniacs["description"] != expected_description:
        print(f"❌ Description mismatch!")
        print(f"   Expected: {expected_description}")
        print(f"   Got: {manga_maniacs['description']}")
        return False
    print(f"✅ Description: {manga_maniacs['description']}")
    
    # Check schedule
    expected_schedule = "Tuesdays, 7:00 PM - 8:00 PM"
    if manga_maniacs["schedule"] != expected_schedule:
        print(f"❌ Schedule mismatch!")
        print(f"   Expected: {expected_schedule}")
        print(f"   Got: {manga_maniacs['schedule']}")
        return False
    print(f"✅ Schedule: {manga_maniacs['schedule']}")
    
    # Check max_participants
    expected_max = 15
    if manga_maniacs["max_participants"] != expected_max:
        print(f"❌ Max participants mismatch!")
        print(f"   Expected: {expected_max}")
        print(f"   Got: {manga_maniacs['max_participants']}")
        return False
    print(f"✅ Max participants: {manga_maniacs['max_participants']}")
    
    # Check participants list exists and is empty
    if "participants" not in manga_maniacs:
        print("❌ Participants field missing!")
        return False
    if not isinstance(manga_maniacs["participants"], list):
        print("❌ Participants should be a list!")
        return False
    if len(manga_maniacs["participants"]) != 0:
        print(f"❌ Participants should be empty initially!")
        return False
    print(f"✅ Participants: {manga_maniacs['participants']} (empty, as expected)")
    
    print("\n🎉 All tests passed!")
    return True

if __name__ == "__main__":
    print("Make sure the FastAPI server is running: uvicorn src.app:app --reload")
    print("Then run this test script.\n")
    
    try:
        success = test_manga_maniacs_exists()
        sys.exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to server. Make sure it's running!")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
