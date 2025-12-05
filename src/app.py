"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, Response
from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime, date, time, timedelta
from collections import defaultdict
import os
import json
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Load activities from JSON file
def load_activities():
    """Load activities from the activities.json file"""
    activities_file = Path(__file__).parent.parent / "activities.json"
    try:
        with open(activities_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise RuntimeError(f"activities.json file not found at {activities_file}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON in activities.json: {e}")

# In-memory activity database (loaded from activities.json)
# Note: Changes to participants are stored in memory only and will be lost on restart.
# To persist changes, you would need to implement a save mechanism.
activities = load_activities()

# In-memory attendance database
# Structure: {activity_name: {date: {email: status}}}
attendance_records = defaultdict(lambda: defaultdict(dict))

# In-memory calendar events database
# Structure: {event_id: event_data}
calendar_events = {}
event_id_counter = 1

# Pydantic models for request/response
class AttendanceRecord(BaseModel):
    email: str
    status: Literal["present", "absent", "excused"]

class CalendarEvent(BaseModel):
    id: Optional[int] = None
    title: str
    activity_name: str
    description: Optional[str] = None
    start: str  # ISO 8601 datetime string
    end: str  # ISO 8601 datetime string
    recurrence: Optional[str] = None  # e.g., "weekly", "daily"
    recurrence_end: Optional[str] = None  # End date for recurring events
    room: Optional[str] = None
    color: Optional[str] = None
    is_cancelled: bool = False
    cancellation_dates: Optional[List[str]] = []  # Specific dates when event is cancelled

class EventCreate(BaseModel):
    title: str
    activity_name: str
    description: Optional[str] = None
    start: str
    end: str
    recurrence: Optional[str] = None
    recurrence_end: Optional[str] = None
    room: Optional[str] = None
    color: Optional[str] = None

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    room: Optional[str] = None
    color: Optional[str] = None
    is_cancelled: Optional[bool] = None

class AttendanceMarkRequest(BaseModel):
    date: str  # Format: YYYY-MM-DD
    records: List[AttendanceRecord]

class AttendanceStats(BaseModel):
    email: str
    total_sessions: int
    present: int
    absent: int
    excused: int
    attendance_percentage: float


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}


# Attendance endpoints
@app.post("/activities/{activity_name}/attendance")
def mark_attendance(activity_name: str, attendance_data: AttendanceMarkRequest):
    """Mark attendance for an activity session"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Validate date format
    try:
        attendance_date = datetime.strptime(attendance_data.date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Don't allow future dates
    if attendance_date > date.today():
        raise HTTPException(status_code=400, detail="Cannot mark attendance for future dates")
    
    activity = activities[activity_name]
    
    # Mark attendance for each student
    for record in attendance_data.records:
        # Validate student is registered for this activity
        if record.email not in activity["participants"]:
            raise HTTPException(
                status_code=400,
                detail=f"Student {record.email} is not registered for {activity_name}"
            )
        
        attendance_records[activity_name][attendance_data.date][record.email] = record.status
    
    return {
        "message": f"Attendance marked for {activity_name} on {attendance_data.date}",
        "records_updated": len(attendance_data.records)
    }


@app.get("/activities/{activity_name}/attendance")
def get_attendance(
    activity_name: str,
    date: Optional[str] = Query(None, description="Specific date (YYYY-MM-DD)")
):
    """Get attendance records for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    if date:
        # Return attendance for specific date
        if date not in attendance_records[activity_name]:
            return {"date": date, "records": []}
        
        records = [
            {"email": email, "status": status}
            for email, status in attendance_records[activity_name][date].items()
        ]
        return {"date": date, "records": records}
    else:
        # Return all attendance records
        all_records = {}
        for record_date, students in attendance_records[activity_name].items():
            all_records[record_date] = [
                {"email": email, "status": status}
                for email, status in students.items()
            ]
        return {"activity": activity_name, "attendance": all_records}


@app.get("/activities/{activity_name}/attendance/stats")
def get_attendance_stats(activity_name: str):
    """Get attendance statistics for all participants in an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    activity = activities[activity_name]
    stats = []
    
    for email in activity["participants"]:
        present_count = 0
        absent_count = 0
        excused_count = 0
        total_sessions = 0
        
        # Count attendance across all dates
        for date_records in attendance_records[activity_name].values():
            if email in date_records:
                total_sessions += 1
                status = date_records[email]
                if status == "present":
                    present_count += 1
                elif status == "absent":
                    absent_count += 1
                elif status == "excused":
                    excused_count += 1
        
        # Calculate percentage (present + excused out of total)
        attendance_percentage = 0.0
        if total_sessions > 0:
            attendance_percentage = ((present_count + excused_count) / total_sessions) * 100
        
        stats.append(AttendanceStats(
            email=email,
            total_sessions=total_sessions,
            present=present_count,
            absent=absent_count,
            excused=excused_count,
            attendance_percentage=round(attendance_percentage, 2)
        ))
    
    return {"activity": activity_name, "statistics": stats}


@app.get("/students/{email}/attendance")
def get_student_attendance(email: str):
    """Get attendance records for a specific student across all activities"""
    student_attendance = {}
    
    for activity_name, activity in activities.items():
        if email in activity["participants"]:
            activity_records = {}
            for record_date, students in attendance_records[activity_name].items():
                if email in students:
                    activity_records[record_date] = students[email]
            
            if activity_records:
                student_attendance[activity_name] = activity_records
    
    if not student_attendance:
        return {
            "email": email,
            "message": "No attendance records found",
            "attendance": {}
        }
    
    return {"email": email, "attendance": student_attendance}


# Calendar endpoints
def parse_datetime(dt_str: str) -> datetime:
    """Parse ISO 8601 datetime string"""
    try:
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid datetime format: {dt_str}")


def check_event_conflicts(start: datetime, end: datetime, room: Optional[str] = None, exclude_event_id: Optional[int] = None) -> List[dict]:
    """Check for scheduling conflicts"""
    conflicts = []
    
    for event_id, event in calendar_events.items():
        if exclude_event_id and event_id == exclude_event_id:
            continue
        
        if event.get("is_cancelled"):
            continue
            
        event_start = parse_datetime(event["start"])
        event_end = parse_datetime(event["end"])
        
        # Check time overlap
        if (start < event_end and end > event_start):
            # If room is specified, only flag if same room
            if room and event.get("room") == room:
                conflicts.append({
                    "event_id": event_id,
                    "title": event["title"],
                    "room": event.get("room"),
                    "start": event["start"],
                    "end": event["end"]
                })
            # Always flag activity conflicts
            elif not room:
                conflicts.append({
                    "event_id": event_id,
                    "title": event["title"],
                    "start": event["start"],
                    "end": event["end"]
                })
    
    return conflicts


def generate_recurring_events(event: dict) -> List[dict]:
    """Generate instances of a recurring event"""
    if not event.get("recurrence"):
        return [event]
    
    events = []
    start_dt = parse_datetime(event["start"])
    end_dt = parse_datetime(event["end"])
    duration = end_dt - start_dt
    
    recurrence_end_dt = parse_datetime(event["recurrence_end"]) if event.get("recurrence_end") else start_dt + timedelta(days=365)
    
    current_dt = start_dt
    cancellation_dates = set(event.get("cancellation_dates", []))
    
    while current_dt <= recurrence_end_dt:
        # Check if this specific date is cancelled
        event_date_str = current_dt.date().isoformat()
        if event_date_str not in cancellation_dates:
            instance = event.copy()
            instance["start"] = current_dt.isoformat()
            instance["end"] = (current_dt + duration).isoformat()
            events.append(instance)
        
        # Move to next occurrence
        if event["recurrence"] == "daily":
            current_dt += timedelta(days=1)
        elif event["recurrence"] == "weekly":
            current_dt += timedelta(weeks=1)
        elif event["recurrence"] == "monthly":
            # Simple monthly recurrence (same day of month)
            if current_dt.month == 12:
                current_dt = current_dt.replace(year=current_dt.year + 1, month=1)
            else:
                current_dt = current_dt.replace(month=current_dt.month + 1)
        else:
            break
    
    return events


@app.post("/calendar/events")
def create_event(event_data: EventCreate):
    """Create a new calendar event"""
    global event_id_counter
    
    # Validate activity exists
    if event_data.activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Parse and validate dates
    start_dt = parse_datetime(event_data.start)
    end_dt = parse_datetime(event_data.end)
    
    if end_dt <= start_dt:
        raise HTTPException(status_code=400, detail="End time must be after start time")
    
    # Check for conflicts
    conflicts = check_event_conflicts(start_dt, end_dt, event_data.room)
    
    event = CalendarEvent(
        id=event_id_counter,
        title=event_data.title,
        activity_name=event_data.activity_name,
        description=event_data.description,
        start=event_data.start,
        end=event_data.end,
        recurrence=event_data.recurrence,
        recurrence_end=event_data.recurrence_end,
        room=event_data.room,
        color=event_data.color or get_activity_color(event_data.activity_name),
        is_cancelled=False,
        cancellation_dates=[]
    )
    
    calendar_events[event_id_counter] = event.dict()
    event_id_counter += 1
    
    return {
        "event": event,
        "conflicts": conflicts,
        "has_conflicts": len(conflicts) > 0
    }


@app.get("/calendar/events")
def get_events(
    start: Optional[str] = Query(None, description="Start date filter (ISO 8601)"),
    end: Optional[str] = Query(None, description="End date filter (ISO 8601)"),
    activity: Optional[str] = Query(None, description="Filter by activity name"),
    email: Optional[str] = Query(None, description="Filter by student email")
):
    """Get calendar events with optional filters"""
    all_events = []
    
    # Generate recurring event instances
    for event_id, event in calendar_events.items():
        event_instances = generate_recurring_events(event)
        all_events.extend(event_instances)
    
    # Apply filters
    filtered_events = all_events
    
    if start:
        start_dt = parse_datetime(start)
        filtered_events = [e for e in filtered_events if parse_datetime(e["end"]) >= start_dt]
    
    if end:
        end_dt = parse_datetime(end)
        filtered_events = [e for e in filtered_events if parse_datetime(e["start"]) <= end_dt]
    
    if activity:
        filtered_events = [e for e in filtered_events if e["activity_name"] == activity]
    
    if email:
        # Filter to events for activities the student is enrolled in
        student_activities = [name for name, details in activities.items() if email in details["participants"]]
        filtered_events = [e for e in filtered_events if e["activity_name"] in student_activities]
    
    return {"events": filtered_events, "count": len(filtered_events)}


@app.get("/calendar/events/{event_id}")
def get_event(event_id: int):
    """Get a specific calendar event"""
    if event_id not in calendar_events:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return calendar_events[event_id]


@app.put("/calendar/events/{event_id}")
def update_event(event_id: int, event_update: EventUpdate):
    """Update a calendar event"""
    if event_id not in calendar_events:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event = calendar_events[event_id]
    
    # Update fields
    if event_update.title is not None:
        event["title"] = event_update.title
    if event_update.description is not None:
        event["description"] = event_update.description
    if event_update.start is not None:
        event["start"] = event_update.start
    if event_update.end is not None:
        event["end"] = event_update.end
    if event_update.room is not None:
        event["room"] = event_update.room
    if event_update.color is not None:
        event["color"] = event_update.color
    if event_update.is_cancelled is not None:
        event["is_cancelled"] = event_update.is_cancelled
    
    # Validate dates if updated
    if event_update.start or event_update.end:
        start_dt = parse_datetime(event["start"])
        end_dt = parse_datetime(event["end"])
        
        if end_dt <= start_dt:
            raise HTTPException(status_code=400, detail="End time must be after start time")
        
        # Check for conflicts
        conflicts = check_event_conflicts(start_dt, end_dt, event.get("room"), exclude_event_id=event_id)
        return {
            "event": event,
            "conflicts": conflicts,
            "has_conflicts": len(conflicts) > 0
        }
    
    return {"event": event}


@app.delete("/calendar/events/{event_id}")
def delete_event(event_id: int):
    """Delete a calendar event"""
    if event_id not in calendar_events:
        raise HTTPException(status_code=404, detail="Event not found")
    
    del calendar_events[event_id]
    return {"message": f"Event {event_id} deleted successfully"}


@app.post("/calendar/events/{event_id}/cancel-date")
def cancel_event_date(event_id: int, date_str: str = Query(..., description="Date to cancel (YYYY-MM-DD)")):
    """Cancel a specific date for a recurring event"""
    if event_id not in calendar_events:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event = calendar_events[event_id]
    
    if not event.get("recurrence"):
        raise HTTPException(status_code=400, detail="Event is not recurring")
    
    # Validate date format
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    if "cancellation_dates" not in event:
        event["cancellation_dates"] = []
    
    if date_str not in event["cancellation_dates"]:
        event["cancellation_dates"].append(date_str)
    
    return {"message": f"Event cancelled for {date_str}", "event": event}


@app.get("/calendar/export")
def export_calendar(
    activity: Optional[str] = Query(None, description="Filter by activity name"),
    email: Optional[str] = Query(None, description="Filter by student email")
):
    """Export calendar events as iCal/ICS format"""
    # Get all events with recurring instances
    all_events = []
    for event_id, event in calendar_events.items():
        event_instances = generate_recurring_events(event)
        all_events.extend(event_instances)
    
    # Apply filters
    filtered_events = all_events
    
    if activity:
        filtered_events = [e for e in filtered_events if e["activity_name"] == activity]
    
    if email:
        # Filter to events for activities the student is enrolled in
        student_activities = [name for name, details in activities.items() if email in details["participants"]]
        filtered_events = [e for e in filtered_events if e["activity_name"] in student_activities]
    
    events = filtered_events
    
    # Generate iCal format
    ical_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Mergington High School//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Mergington High School Activities",
        "X-WR-TIMEZONE:UTC"
    ]
    
    for event in events:
        start_dt = parse_datetime(event["start"])
        end_dt = parse_datetime(event["end"])
        
        # Format dates for iCal (YYYYMMDDTHHMMSSZ)
        start_ical = start_dt.strftime("%Y%m%dT%H%M%SZ")
        end_ical = end_dt.strftime("%Y%m%dT%H%M%SZ")
        
        ical_lines.extend([
            "BEGIN:VEVENT",
            f"UID:{event['id']}@mergington.edu",
            f"DTSTART:{start_ical}",
            f"DTEND:{end_ical}",
            f"SUMMARY:{event['title']}",
            f"DESCRIPTION:{event.get('description', '')}",
            f"LOCATION:{event.get('room', '')}",
            "STATUS:CONFIRMED",
            "END:VEVENT"
        ])
    
    ical_lines.append("END:VCALENDAR")
    
    ical_content = "\r\n".join(ical_lines)
    
    return Response(
        content=ical_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": "attachment; filename=mergington-calendar.ics"
        }
    )


def get_activity_color(activity_name: str) -> str:
    """Get a consistent color for an activity"""
    colors = [
        "#3788d8",  # Blue
        "#dc3545",  # Red
        "#28a745",  # Green
        "#ffc107",  # Yellow
        "#6f42c1",  # Purple
        "#fd7e14",  # Orange
        "#20c997",  # Teal
        "#e83e8c"   # Pink
    ]
    # Use hash of activity name to get consistent color
    index = hash(activity_name) % len(colors)
    return colors[index]
