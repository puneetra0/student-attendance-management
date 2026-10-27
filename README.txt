# Student Online Attendance Management System

A Python 3 DSA mini-project demonstrating student records, attendance marking, summaries, CSV exports, and a local HTML dashboard.

## Features
- Student directory and search by name/roll number
- Mark attendance as Present, Absent, or Late
- Attendance percentage summary (Late counts as attended)
- CSV export: `data/attendance_records.csv` and `data/attendance_summary.csv`
- Dark, responsive HTML dashboard: `data/attendance_dashboard.html`
- Full demonstration mode for quick testing

## DSA concepts
- **List:** student records and search results
- **Dictionary:** O(1)-average roll-number lookup and date-wise attendance maps
- **Deque (queue):** processes the student list sequentially during the demo
- **Sorting:** records are exported in sorted date/roll order
- **Linear search:** searches students by partial name or roll number

## Run in VS Code (Mac)
1. Extract the ZIP.
2. Open the extracted `Student_Online_Attendance_Management_System` folder in VS Code.
3. Choose **Terminal → New Terminal**.
4. Run:
   ```bash
   python3 attendance_management.py
   ```
5. Enter `7` for the full demonstration.
6. Open `data/attendance_dashboard.html` in your browser.

No pip install is needed. The project uses only the Python standard library.

## Important
This is an offline academic prototype, not a deployed online attendance service. It uses fictional demonstration data. For a real multi-user online system, authentication, a database, access control, and secure hosting would need to be added.
