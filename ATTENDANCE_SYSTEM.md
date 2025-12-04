# Attendance Tracking System Documentation

## Overview
The Attendance Tracking System allows teachers and administrators to mark and monitor student attendance for extracurricular activities.

## New API Endpoints

### 1. Mark Attendance
**POST** `/activities/{activity_name}/attendance`

Mark attendance for a specific activity session.

**Request Body:**
```json
{
  "date": "2024-12-04",
  "records": [
    {
      "email": "student@mergington.edu",
      "status": "present"
    }
  ]
}
```

**Status Options:**
- `present` - Student attended
- `absent` - Student did not attend
- `excused` - Student was absent with valid excuse

**Response:**
```json
{
  "message": "Attendance marked for Chess Club on 2024-12-04",
  "records_updated": 2
}
```

### 2. Get Attendance Records
**GET** `/activities/{activity_name}/attendance?date=YYYY-MM-DD`

Retrieve attendance records for an activity.

**Query Parameters:**
- `date` (optional) - Get attendance for specific date

**Response (with date):**
```json
{
  "date": "2024-12-04",
  "records": [
    {
      "email": "student@mergington.edu",
      "status": "present"
    }
  ]
}
```

**Response (without date - all records):**
```json
{
  "activity": "Chess Club",
  "attendance": {
    "2024-12-01": [...],
    "2024-12-04": [...]
  }
}
```

### 3. Get Attendance Statistics
**GET** `/activities/{activity_name}/attendance/stats`

Get attendance statistics for all participants in an activity.

**Response:**
```json
{
  "activity": "Chess Club",
  "statistics": [
    {
      "email": "student@mergington.edu",
      "total_sessions": 10,
      "present": 8,
      "absent": 1,
      "excused": 1,
      "attendance_percentage": 90.0
    }
  ]
}
```

### 4. Get Student Attendance
**GET** `/students/{email}/attendance`

Get attendance records for a specific student across all their activities.

**Response:**
```json
{
  "email": "student@mergington.edu",
  "attendance": {
    "Chess Club": {
      "2024-12-01": "present",
      "2024-12-04": "present"
    },
    "Programming Class": {
      "2024-12-03": "absent"
    }
  }
}
```

## Features Implemented

✅ **Manual Attendance Marking**
- Teachers can mark attendance for each session
- Date and time stamping
- Mark present/absent/excused

✅ **Attendance Reports**
- Daily attendance view
- View all attendance records for an activity
- Individual student attendance history
- Percentage calculations

✅ **Validation**
- Cannot mark attendance for future dates
- Cannot mark attendance for unregistered students
- Validates date format
- Validates activity exists

## Future Enhancements (Not in this PR)

The following features are planned for future releases:
- Automated check-in options (QR code, WiFi-based)
- Email notifications for absences
- Export to CSV/PDF
- Mobile app support
- Database persistence (Issue #3)

## Testing

To test the endpoints, you can:

1. Start the server:
   ```bash
   uvicorn src.app:app --reload
   ```

2. Run the test script:
   ```bash
   python test_attendance.py
   ```

3. Or use the interactive API docs:
   - Navigate to `http://localhost:8000/docs`
   - Try out the new attendance endpoints

## Example Usage

### Mark attendance for today's session:
```bash
curl -X POST "http://localhost:8000/activities/Chess%20Club/attendance" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-12-04",
    "records": [
      {"email": "michael@mergington.edu", "status": "present"},
      {"email": "daniel@mergington.edu", "status": "present"}
    ]
  }'
```

### Get attendance statistics:
```bash
curl "http://localhost:8000/activities/Chess%20Club/attendance/stats"
```

### Get a student's attendance:
```bash
curl "http://localhost:8000/students/michael@mergington.edu/attendance"
```
