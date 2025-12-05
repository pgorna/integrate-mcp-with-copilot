# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- **Easy activity management** - Activities are stored in `activities.json` file for easy editing
- **📅 Calendar View** - Visual calendar with month/week/day views
- **Event Scheduling** - Create and manage calendar events with recurring patterns
- **iCal Export** - Download calendar events for Google Calendar, Outlook, etc.
- **Conflict Detection** - Automatic detection of scheduling conflicts
- **Attendance Tracking** - Mark and track student attendance

## Calendar Features

The application now includes a comprehensive calendar system! See [CALENDAR_FEATURES.md](../CALENDAR_FEATURES.md) for detailed documentation.

### Quick Start with Calendar
```bash
# Start the server
uvicorn src.app:app --reload

# Populate sample events
python3 populate_calendar.py

# Visit http://localhost:8000 and click "Calendar View"
```

### Key Calendar Capabilities
- 📅 **Visual Interface**: Interactive calendar with month, week, and day views
- 🔁 **Recurring Events**: Daily, weekly, or monthly recurrence patterns
- 🔍 **Smart Filtering**: Filter by activity or student email
- 📥 **iCal Export**: Download events for import into any calendar app
- ⚠️ **Conflict Detection**: Automatic warnings for scheduling conflicts
- 📍 **Room Booking**: Track and manage room assignments
- ⏰ **Upcoming Events**: Widget showing next 5 events

## Managing Activities

Activities are now stored in the `activities.json` file in the repository root. Teachers can easily add, remove, or modify activities by editing this file without touching the Python code.

### Example activity entry:
```json
{
    "Activity Name": {
        "description": "Activity description",
        "schedule": "When it meets",
        "max_participants": 20,
        "participants": []
    }
}
```

**Note:** After modifying `activities.json`, restart the server to load the changes.

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

### Activities
| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Unregister from an activity                                    |

### Calendar Events
| Method | Endpoint                                    | Description                                  |
| ------ | ------------------------------------------- | -------------------------------------------- |
| GET    | `/calendar/events`                          | Get all calendar events with filters         |
| POST   | `/calendar/events`                          | Create a new calendar event                  |
| GET    | `/calendar/events/{event_id}`               | Get a specific event                         |
| PUT    | `/calendar/events/{event_id}`               | Update an event                              |
| DELETE | `/calendar/events/{event_id}`               | Delete an event                              |
| POST   | `/calendar/events/{event_id}/cancel-date`   | Cancel specific date for recurring event     |
| GET    | `/calendar/export`                          | Export calendar as iCal (.ics) file          |

### Attendance
| Method | Endpoint                                    | Description                                  |
| ------ | ------------------------------------------- | -------------------------------------------- |
| POST   | `/activities/{activity_name}/attendance`    | Mark attendance for an activity session      |
| GET    | `/activities/{activity_name}/attendance`    | Get attendance records                       |
| GET    | `/activities/{activity_name}/attendance/stats` | Get attendance statistics                 |
| GET    | `/students/{email}/attendance`              | Get attendance for a specific student        |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All data is stored in memory, which means data will be reset when the server restarts.
