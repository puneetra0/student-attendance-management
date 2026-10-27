"""
STUDENT ONLINE ATTENDANCE MANAGEMENT SYSTEM
DSA mini project in Python 3.

This is an offline educational prototype. It stores records in memory while running,
exports attendance records to CSV, and generates a local HTML dashboard.
No third-party packages are required.
"""

from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import date, datetime
import csv
import html
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
ATTENDANCE_CSV = DATA_DIR / "attendance_records.csv"
SUMMARY_CSV = DATA_DIR / "attendance_summary.csv"
DASHBOARD_HTML = DATA_DIR / "attendance_dashboard.html"


@dataclass
class Student:
    roll_no: str
    name: str
    course: str


class AttendanceSystem:
    def __init__(self):
        self.students = [
            Student("AIML001", "Aarav Sharma", "CSE-AIML"),
            Student("AIML002", "Diya Verma", "CSE-AIML"),
            Student("AIML003", "Kabir Singh", "CSE-AIML"),
            Student("CSE004", "Meera Gupta", "CSE"),
            Student("CSE005", "Arjun Mehta", "CSE"),
            Student("DS006", "Ananya Rao", "Data Science"),
            Student("DS007", "Vivaan Jain", "Data Science"),
            Student("CSE008", "Sara Khan", "CSE"),
        ]
        # Dictionary provides fast lookup by roll number.
        self.student_by_roll = {s.roll_no: s for s in self.students}
        # Date -> roll number -> status (Present / Absent / Late).
        self.records = defaultdict(dict)
        self._load_sample_attendance()

    def _load_sample_attendance(self):
        """Create repeatable fictional demonstration records for the previous days."""
        sample = {
            "AIML001": ["P", "P", "P", "A", "P"],
            "AIML002": ["P", "A", "P", "P", "P"],
            "AIML003": ["P", "P", "L", "P", "A"],
            "CSE004":  ["A", "P", "P", "P", "P"],
            "CSE005":  ["P", "P", "A", "P", "P"],
            "DS006":   ["P", "P", "P", "P", "A"],
            "DS007":   ["P", "L", "P", "A", "P"],
            "CSE008":  ["P", "P", "P", "P", "P"],
        }
        today = date.today()
        for offset in range(5, 0, -1):
            day = (today.fromordinal(today.toordinal() - offset)).isoformat()
            for roll, statuses in sample.items():
                code = statuses[5 - offset]
                self.records[day][roll] = {"P": "Present", "A": "Absent", "L": "Late"}[code]

    def mark_attendance(self, day, roll, status):
        if roll not in self.student_by_roll:
            raise ValueError(f"Unknown roll number: {roll}")
        if status not in {"Present", "Absent", "Late"}:
            raise ValueError("Status must be Present, Absent, or Late.")
        self.records[day][roll] = status

    def attendance_stats(self, roll, through_date=None):
        total = present = late = 0
        for day, day_records in self.records.items():
            if through_date and day > through_date:
                continue
            if roll in day_records:
                total += 1
                if day_records[roll] == "Present":
                    present += 1
                elif day_records[roll] == "Late":
                    late += 1
        attended = present + late
        percentage = (attended / total * 100) if total else 0.0
        return total, present, late, total - present - late, percentage

    def mark_today_for_demo(self):
        today = date.today().isoformat()
        # Deque is used as a queue to process each student once in sequence.
        queue = deque(s.roll_no for s in self.students)
        statuses = ["Present", "Present", "Absent", "Late", "Present", "Present", "Absent", "Present"]
        index = 0
        while queue:
            roll = queue.popleft()
            self.mark_attendance(today, roll, statuses[index % len(statuses)])
            index += 1
        return today

    def list_students(self):
        print("\n" + "=" * 72)
        print(" STUDENT DIRECTORY")
        print("=" * 72)
        print(f"{'ROLL NO.':<13}{'STUDENT NAME':<23}{'COURSE':<20}")
        print("-" * 72)
        for s in self.students:
            print(f"{s.roll_no:<13}{s.name:<23}{s.course:<20}")
        print(f"\nTotal students: {len(self.students)}")

    def report(self):
        print("\n" + "=" * 88)
        print(" ATTENDANCE SUMMARY")
        print("=" * 88)
        print(f"{'ROLL NO.':<12}{'NAME':<20}{'CLASSES':>9}{'PRESENT':>10}{'LATE':>7}{'ABSENT':>9}{'ATTENDANCE':>14}")
        print("-" * 88)
        for s in self.students:
            total, present, late, absent, pct = self.attendance_stats(s.roll_no)
            print(f"{s.roll_no:<12}{s.name:<20}{total:>9}{present:>10}{late:>7}{absent:>9}{pct:>13.1f}%")
        print("-" * 88)
        print("Note: Late arrivals count as attended for the percentage.")

    def search_student(self, query):
        query = query.strip().lower()
        matches = [s for s in self.students if query in s.roll_no.lower() or query in s.name.lower()]
        if not matches:
            print(f"No students found for '{query}'.")
            return
        print("\nSEARCH RESULTS")
        for s in matches:
            total, present, late, absent, pct = self.attendance_stats(s.roll_no)
            print(f"{s.roll_no:<12} {s.name:<20} {s.course:<16} Attendance: {pct:.1f}% ({total} classes)")

    def export_csv(self):
        with ATTENDANCE_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Roll Number", "Student Name", "Course", "Status"])
            for day in sorted(self.records):
                for roll, status in sorted(self.records[day].items()):
                    s = self.student_by_roll.get(roll)
                    if s:
                        writer.writerow([day, roll, s.name, s.course, status])
        with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Roll Number", "Student Name", "Course", "Classes Recorded", "Present", "Late", "Absent", "Attendance Percentage"])
            for s in self.students:
                total, present, late, absent, pct = self.attendance_stats(s.roll_no)
                writer.writerow([s.roll_no, s.name, s.course, total, present, late, absent, f"{pct:.1f}"])
        return ATTENDANCE_CSV, SUMMARY_CSV

    def generate_dashboard(self):
        today = date.today().isoformat()
        rows = []
        for s in self.students:
            total, present, late, absent, pct = self.attendance_stats(s.roll_no)
            color = "#16a34a" if pct >= 75 else "#ea580c"
            rows.append(
                f"<tr><td>{html.escape(s.roll_no)}</td><td>{html.escape(s.name)}</td>"
                f"<td>{html.escape(s.course)}</td><td>{total}</td><td>{present}</td>"
                f"<td>{late}</td><td>{absent}</td><td><span class='pill' style='color:{color}'>{pct:.1f}%</span></td></tr>"
            )
        total_records = sum(len(v) for v in self.records.values())
        html_doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Student Attendance Dashboard</title>
<style>
:root{{--bg:#0b1020;--panel:#131b2e;--line:#26334d;--text:#edf2ff;--muted:#98a6c5;--cyan:#67e8f9}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at top right,#1b2d4d,#0b1020 55%);font:15px/1.5 -apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;color:var(--text);padding:34px}}
.wrap{{max-width:1120px;margin:auto}}.eyebrow{{color:var(--cyan);letter-spacing:2px;font-size:12px;font-weight:700}}
h1{{font-size:34px;margin:7px 0}}.sub{{color:var(--muted);margin-bottom:26px}}
.cards{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:24px 0}}
.card{{background:rgba(19,27,46,.94);border:1px solid var(--line);padding:20px;border-radius:16px}}
.label{{color:var(--muted);font-size:13px}}.value{{font-size:28px;font-weight:750;margin-top:6px}}
.tablebox{{overflow:auto;background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:6px}}
table{{width:100%;border-collapse:collapse;min-width:760px}}th,td{{text-align:left;padding:14px 12px;border-bottom:1px solid var(--line)}}
th{{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.7px}}tr:last-child td{{border:0}}
.pill{{font-weight:750;background:#1d2a40;padding:5px 9px;border-radius:20px}}
footer{{color:var(--muted);font-size:12px;margin-top:18px}}@media(max-width:700px){{body{{padding:18px}}.cards{{grid-template-columns:1fr}}h1{{font-size:27px}}}}
</style></head><body><main class="wrap">
<div class="eyebrow">ACADEMIC TOOLS / ATTENDANCE</div><h1>Student Attendance</h1>
<div class="sub">Overview of sample attendance records · Generated {today}</div>
<section class="cards"><div class="card"><div class="label">Registered students</div><div class="value">{len(self.students)}</div></div>
<div class="card"><div class="label">Attendance entries</div><div class="value">{total_records}</div></div>
<div class="card"><div class="label">Minimum target</div><div class="value">75%</div></div></section>
<div class="tablebox"><table><thead><tr><th>Roll no.</th><th>Student</th><th>Course</th><th>Classes</th><th>Present</th><th>Late</th><th>Absent</th><th>Attendance</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
<footer>Offline educational prototype · Sample student data is fictional · Late arrivals count as attended.</footer>
</main></body></html>"""
        DASHBOARD_HTML.write_text(html_doc, encoding="utf-8")
        return DASHBOARD_HTML

    def full_demo(self):
        day = self.mark_today_for_demo()
        self.list_students()
        print(f"\nDemo attendance recorded for {day}.")
        self.report()
        files = self.export_csv()
        dashboard = self.generate_dashboard()
        print("\n" + "=" * 72)
        print(" FILES GENERATED SUCCESSFULLY")
        print("=" * 72)
        for p in (*files, dashboard):
            print(f"✓ {p.relative_to(APP_DIR)}")
        print("\nDemo complete. Open data/attendance_dashboard.html in your browser to view the dashboard.")

    def menu(self):
        while True:
            print("\n" + "═" * 54)
            print("       STUDENT ATTENDANCE MANAGEMENT SYSTEM")
            print("═" * 54)
            print("  1. View student directory")
            print("  2. Mark today's attendance")
            print("  3. View attendance summary")
            print("  4. Search student")
            print("  5. Export attendance CSV files")
            print("  6. Generate HTML dashboard")
            print("  7. Run full demonstration")
            print("  0. Exit")
            choice = input("\nChoose an option: ").strip()
            try:
                if choice == "1":
                    self.list_students()
                elif choice == "2":
                    day = date.today().isoformat()
                    print(f"Marking attendance for {day}. Enter P=Present, A=Absent, L=Late.")
                    for s in self.students:
                        answer = input(f"{s.roll_no} | {s.name}: ").strip().upper()
                        status = {"P": "Present", "A": "Absent", "L": "Late"}.get(answer)
                        if status:
                            self.mark_attendance(day, s.roll_no, status)
                        else:
                            print("Invalid status; this student's existing record was not changed.")
                elif choice == "3":
                    self.report()
                elif choice == "4":
                    self.search_student(input("Enter a name or roll number: "))
                elif choice == "5":
                    for p in self.export_csv():
                        print(f"Exported: {p.relative_to(APP_DIR)}")
                elif choice == "6":
                    print(f"Dashboard created: {self.generate_dashboard().relative_to(APP_DIR)}")
                elif choice == "7":
                    self.full_demo()
                elif choice == "0":
                    print("Thank you for using Student Attendance Management System.")
                    break
                else:
                    print("Invalid option. Choose 0 to 7.")
            except (OSError, ValueError) as exc:
                print(f"Error: {exc}")


def main():
    AttendanceSystem().menu()


if __name__ == "__main__":
    main()
