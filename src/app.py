"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime, date
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
activities = load_activities()

# In-memory attendance database
# Structure: {activity_name: {date: {email: status}}}
attendance_records = defaultdict(lambda: defaultdict(dict))

# Pydantic models for request/response
class AttendanceRecord(BaseModel):
    email: str
    status: Literal["present", "absent", "excused"]

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
