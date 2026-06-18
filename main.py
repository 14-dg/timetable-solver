"""
Run the timetable solver and print a formatted schedule.

Usage:
    python main.py
    python main.py data/sample_data.json
"""

import sys
from pathlib import Path
from collections import defaultdict

from solver import solve


DAYS_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


def print_schedule(schedule, unscheduled):
    # Group by day → timeslot
    by_day = defaultdict(list)
    for entry in schedule:
        by_day[entry.timeslot.day].append(entry)

    print("\n" + "=" * 70)
    print("  GENERATED TIMETABLE")
    print("=" * 70)

    for day in DAYS_ORDER:
        entries = sorted(by_day.get(day, []), key=lambda e: e.timeslot.start)
        if not entries:
            continue
        print(f"\n── {day} " + "─" * (62 - len(day)))
        for e in entries:
            print(
                f"  {e.timeslot.start}–{e.timeslot.end}  "
                f"{e.course.name:<35} "
                f"{e.room.name:<10} "
                f"{e.lecturer.name}"
            )

    print("\n" + "=" * 70)
    print(f"  Total sessions scheduled: {len(schedule)}")

    if unscheduled:
        print(f"\n⚠  Unscheduled courses ({len(unscheduled)}):")
        for c in unscheduled:
            print(f"   - {c.name}")
    else:
        print("  ✓ All courses successfully scheduled")
    print("=" * 70 + "\n")


def main():
    data_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/sample_data.json")

    if not data_path.exists():
        print(f"Error: data file not found at {data_path}")
        sys.exit(1)

    print(f"Loading data from {data_path} ...")
    schedule, unscheduled = solve(data_path)
    print_schedule(schedule, unscheduled)


if __name__ == "__main__":
    main()
