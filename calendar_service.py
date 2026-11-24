"""Google Calendar operations module for event listing, slot finding, and creation.

Time zone: Asia/Jerusalem. Never deletes any events. File under 150 lines.
"""

from __future__ import annotations

from datetime import datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from dateutil import parser as dt_parser

from auth import get_calendar_service

JERUSALEM_TZ = ZoneInfo("Asia/Jerusalem")


def list_events_impl(days_ahead: int = 7) -> list[dict[str, Any]]:
    """List upcoming events within the specified number of days ahead."""
    service = get_calendar_service()
    now = datetime.now(JERUSALEM_TZ)
    time_min = now.isoformat()
    time_max = (now + timedelta(days=max(1, days_ahead))).isoformat()

    events_res = service.events().list(
        calendarId="primary",
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    items = events_res.get("items", [])
    results = []
    for item in items:
        results.append({
            "id": item.get("id"),
            "summary": item.get("summary", "(No Title)"),
            "start": item.get("start", {}).get("dateTime") or item.get("start", {}).get("date"),
            "end": item.get("end", {}).get("dateTime") or item.get("end", {}).get("date"),
            "description": item.get("description", ""),
            "location": item.get("location", ""),
        })
    return results


def find_free_slots_impl(date: str, duration_minutes: int = 30) -> list[dict[str, Any]]:
    """Find available free time slots between 08:00 and 18:00 for a given date."""
    service = get_calendar_service()
    target_date = dt_parser.parse(date).date()
    day_start = datetime.combine(target_date, time(8, 0), tzinfo=JERUSALEM_TZ)
    day_end = datetime.combine(target_date, time(18, 0), tzinfo=JERUSALEM_TZ)

    body = {
        "timeMin": day_start.isoformat(),
        "timeMax": day_end.isoformat(),
        "timeZone": "Asia/Jerusalem",
        "items": [{"id": "primary"}],
    }
    fb_res = service.freebusy().query(body=body).execute()
    busy_list = fb_res.get("calendars", {}).get("primary", {}).get("busy", [])

    # Sort and merge busy intervals
    parsed_busy = []
    for b in busy_list:
        b_start = dt_parser.isoparse(b["start"]).astimezone(JERUSALEM_TZ)
        b_end = dt_parser.isoparse(b["end"]).astimezone(JERUSALEM_TZ)
        parsed_busy.append((max(day_start, b_start), min(day_end, b_end)))
    parsed_busy.sort(key=lambda x: x[0])

    slot_delta = timedelta(minutes=max(10, duration_minutes))
    free_slots = []
    current_pointer = day_start

    for b_start, b_end in parsed_busy:
        if b_start > current_pointer:
            gap = b_start - current_pointer
            if gap >= slot_delta:
                free_slots.append({
                    "start": current_pointer.isoformat(),
                    "end": b_start.isoformat(),
                    "available_minutes": int(gap.total_seconds() // 60),
                })
        if b_end > current_pointer:
            current_pointer = b_end

    if current_pointer < day_end:
        gap = day_end - current_pointer
        if gap >= slot_delta:
            free_slots.append({
                "start": current_pointer.isoformat(),
                "end": day_end.isoformat(),
                "available_minutes": int(gap.total_seconds() // 60),
            })

    return free_slots


def create_event_impl(
    title: str, start: str, end: str, description: str = ""
) -> dict[str, Any]:
    """Create a new event in Google Calendar within Asia/Jerusalem timezone."""
    service = get_calendar_service()

    # Parse and ensure datetime is timezone-aware in Asia/Jerusalem
    dt_start = dt_parser.parse(start)
    if dt_start.tzinfo is None:
        dt_start = dt_start.replace(tzinfo=JERUSALEM_TZ)
    else:
        dt_start = dt_start.astimezone(JERUSALEM_TZ)

    dt_end = dt_parser.parse(end)
    if dt_end.tzinfo is None:
        dt_end = dt_end.replace(tzinfo=JERUSALEM_TZ)
    else:
        dt_end = dt_end.astimezone(JERUSALEM_TZ)

    event_body = {
        "summary": title,
        "description": description,
        "start": {"dateTime": dt_start.isoformat(), "timeZone": "Asia/Jerusalem"},
        "end": {"dateTime": dt_end.isoformat(), "timeZone": "Asia/Jerusalem"},
    }

    event = service.events().insert(calendarId="primary", body=event_body).execute()

    return {
        "status": "created",
        "id": event.get("id"),
        "summary": event.get("summary"),
        "start": event.get("start", {}).get("dateTime"),
        "end": event.get("end", {}).get("dateTime"),
        "htmlLink": event.get("htmlLink", ""),
    }
