# Calendar View and Scheduling Features

## Overview
The Mergington High School Activities system now includes a comprehensive calendar view and scheduling features to help students, parents, and staff view and manage activity schedules.

## Features Implemented

### 1. Visual Calendar Interface
- **Multiple Views**: Month, week, and day views powered by FullCalendar.js
- **Color-Coded Events**: Each activity type is automatically assigned a unique color
- **Interactive Events**: Click on any event to view detailed information
- **Responsive Design**: Works seamlessly on desktop and mobile devices

### 2. Calendar Navigation
- Easy switching between List View and Calendar View
- View switcher buttons in the header
- Maintains all existing list view functionality

### 3. Filtering and Search
- **Filter by Activity**: Select specific activities from the dropdown
- **Filter by Student**: Enter a student email to see only their enrolled activities
- **Date Range Filtering**: Automatically filters events based on the calendar view
- **Apply/Clear Filters**: Easy-to-use filter controls

### 4. Schedule Management
- **Create Events**: Calendar events can be created via API
- **Recurring Events**: Support for daily, weekly, and monthly recurring events
- **Event Exceptions**: Cancel specific dates for recurring events (holidays, etc.)
- **Room/Resource Booking**: Track room assignments for each event
- **Conflict Detection**: Automatic detection of scheduling conflicts

### 5. Calendar Integration
- **iCal Export**: Download calendar as .ics file for import into other applications
- **Calendar Feeds**: Subscribe to activity calendars via iCal format
- **Import to Google Calendar**: Export and import into Google Calendar
- **Import to Outlook**: Export and import into Outlook Calendar

### 6. Upcoming Events Widget
- Shows the next 5 upcoming events
- Displays event date, time, and location
- Automatically updates based on filters
- Refreshes every 5 minutes

## API Endpoints

### Calendar Events

#### Create Event
```
POST /calendar/events
```
**Body:**
```json
{
  "title": "Chess Club Meeting",
  "activity_name": "Chess Club",
  "description": "Weekly chess practice",
  "start": "2024-12-06T15:30:00",
  "end": "2024-12-06T17:00:00",
  "room": "Room 101",
  "recurrence": "weekly",
  "recurrence_end": "2025-01-31T17:00:00",
  "color": "#3788d8"
}
```

**Response:**
```json
{
  "event": { /* event object */ },
  "conflicts": [ /* array of conflicting events */ ],
  "has_conflicts": false
}
```

#### Get Events
```
GET /calendar/events?start={ISO8601}&end={ISO8601}&activity={name}&email={student}
```

**Query Parameters:**
- `start` (optional): Start date filter (ISO 8601 format)
- `end` (optional): End date filter (ISO 8601 format)
- `activity` (optional): Filter by activity name
- `email` (optional): Filter by student email (shows only their enrolled activities)

**Response:**
```json
{
  "events": [ /* array of events */ ],
  "count": 5
}
```

#### Get Single Event
```
GET /calendar/events/{event_id}
```

#### Update Event
```
PUT /calendar/events/{event_id}
```
**Body:**
```json
{
  "title": "Updated Title",
  "start": "2024-12-07T15:30:00",
  "end": "2024-12-07T17:00:00",
  "room": "Room 202",
  "is_cancelled": false
}
```

#### Delete Event
```
DELETE /calendar/events/{event_id}
```

#### Cancel Recurring Event Date
```
POST /calendar/events/{event_id}/cancel-date?date_str=2024-12-25
```

#### Export Calendar
```
GET /calendar/export?activity={name}&email={student}
```

Returns an iCal (.ics) file that can be imported into calendar applications.

## Usage Examples

### Creating a One-Time Event
```python
import requests

event = {
    "title": "Chess Tournament",
    "activity_name": "Chess Club",
    "description": "Annual school chess tournament",
    "start": "2024-12-15T09:00:00",
    "end": "2024-12-15T17:00:00",
    "room": "Auditorium"
}

response = requests.post("http://localhost:8000/calendar/events", json=event)
print(response.json())
```

### Creating a Recurring Event
```python
event = {
    "title": "Programming Class",
    "activity_name": "Programming Class",
    "description": "Weekly programming lessons",
    "start": "2024-12-03T15:30:00",
    "end": "2024-12-03T16:30:00",
    "recurrence": "weekly",
    "recurrence_end": "2025-05-30T16:30:00",
    "room": "Computer Lab"
}

response = requests.post("http://localhost:8000/calendar/events", json=event)
```

### Cancelling a Specific Date
```python
# Cancel class on Christmas
response = requests.post(
    "http://localhost:8000/calendar/events/2/cancel-date",
    params={"date_str": "2024-12-25"}
)
```

### Exporting Student's Calendar
```python
# Export calendar for a specific student
url = "http://localhost:8000/calendar/export?email=emma@mergington.edu"
# Download and import the .ics file into Google Calendar or Outlook
```

## Frontend Usage

### View Switcher
Users can switch between List View and Calendar View using the buttons in the header.

### Calendar Filters
1. Select an activity from the dropdown to view only that activity's events
2. Enter a student email to view only events for activities they're enrolled in
3. Click "Apply Filters" to update the calendar
4. Click "Clear Filters" to reset

### Event Details
Click on any calendar event to view detailed information including:
- Activity name
- Start and end times
- Room location
- Description
- Cancellation status

### Export Calendar
Click the "📥 Export to iCal" button to download the calendar as an .ics file. This file can be imported into:
- Google Calendar
- Microsoft Outlook
- Apple Calendar
- Any iCal-compatible application

## Technical Details

### Dependencies
- **FullCalendar.js 6.1.10**: Provides the interactive calendar interface
- **FastAPI**: Backend API framework
- **Python datetime**: Date/time handling

### Data Models
- **CalendarEvent**: Main event model with support for recurrence
- **EventCreate**: Model for creating new events
- **EventUpdate**: Model for updating existing events

### Conflict Detection
The system automatically checks for scheduling conflicts based on:
- Time overlap between events
- Room availability (if room is specified)

Conflicts are returned when creating or updating events, but do not prevent the operation (warnings only).

### Recurring Events
Recurring events are expanded into individual instances when queried. The system supports:
- **Daily**: Events that occur every day
- **Weekly**: Events that occur every week on the same day
- **Monthly**: Events that occur on the same date each month

Specific dates can be cancelled without affecting the entire recurrence pattern.

## Testing

Run the test scripts to verify functionality:

```bash
# Test calendar endpoints
python3 test_calendar.py

# Populate sample events
python3 populate_calendar.py
```

## Future Enhancements

Potential future improvements:
- Email/SMS reminders for upcoming events
- Drag-and-drop event rescheduling (admin mode)
- Mobile app integration
- Real-time calendar sync
- Event attendance tracking integration
- Waitlist management for full events

## Screenshots

### List View
Shows all activities in card format with participants and registration options.

### Calendar View
Interactive calendar showing scheduled events color-coded by activity type.

### Event Details Modal
Popup showing detailed information when clicking on a calendar event.

## Support

For issues or questions about the calendar features, please contact the development team.
