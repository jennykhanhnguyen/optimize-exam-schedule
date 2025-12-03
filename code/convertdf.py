import re
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent


def read_lines(path: Path) -> list[str]:
    """Return non-empty, stripped lines from a text file."""
    text = path.read_text(errors="ignore")
    return [line.rstrip("\n") for line in text.splitlines() if line.strip()]


def parse_sections(lines: list[str]) -> dict[str, list[str]]:
    """Split the data file into sections using known headings."""
    headers = {
        "DATES",
        "TIMES",
        "ROOMS",
        "ROOM ASSIGNMENTS",
        "COINCIDENCES",
        "EARLINESS PRIORITY (1-100)",
        "MISC",
    }
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if line in headers:
            current = line
            sections[current] = []
            continue
        if set(line) == {"-"}:
            continue
        if current:
            sections[current].append(line)
    return sections


# ============================================================
# 1. STUDENTS FILE (student, course)
# ============================================================
students_raw = read_lines(BASE_DIR / "students")
student_pattern = re.compile(r"^(\S+)\s+(\S+)$")
students_data = []
for line in students_raw:
    m = student_pattern.match(line)
    if m:
        students_data.append({"student": m.group(1), "course": m.group(2)})

df_students = pd.DataFrame(students_data)
print(f"Students: {len(df_students)} rows")
print(df_students.head(), "\n")


# ============================================================
# 2. ENROLMENTS FILE (student, exam)
# ============================================================
enrol_raw = read_lines(BASE_DIR / "enrolements")
enrol_pattern = re.compile(r"^(\S+)\s+(\S+)$")
enrol_data = []
for line in enrol_raw:
    m = enrol_pattern.match(line)
    if m:
        enrol_data.append({"student": m.group(1), "exam": m.group(2)})

df_enrolments = pd.DataFrame(enrol_data)
print(f"Enrolments: {len(df_enrolments)} rows")
print(df_enrolments.head(), "\n")


# ============================================================
# 3. EXAMS FILE (exam, title, duration, dept)
# Example line:
# AA2016E1 OPERA STUDIES, I                         1:30 GM
# ============================================================
exam_raw = read_lines(BASE_DIR / "exams")
exam_pattern = re.compile(r"^(\S+)\s+(.+?)\s+(\d+:\d+)\s+([A-Z]+\*?)$")
exam_data = []
for line in exam_raw:
    m = exam_pattern.match(line)
    if m:
        exam_data.append(
            {
                "exam": m.group(1),
                "title": m.group(2).strip(),
                "duration": m.group(3),
                "dept": m.group(4),
            }
        )

df_exams = pd.DataFrame(exam_data)
print(f"Exams: {len(df_exams)} rows")
print(df_exams.head(), "\n")


# ============================================================
# 4. DATA FILE (dates, times, rooms, special rules)
# ============================================================
data_raw = read_lines(BASE_DIR / "data")
sections = parse_sections(data_raw)

# ---- Parse rooms ----
rooms = []
for line in sections.get("ROOMS", []):
    m = re.match(r"^(?P<room>\S+)\s+(?P<capacity>\d+)", line)
    if m:
        rooms.append({"room": m.group("room"), "capacity": int(m.group("capacity"))})
df_rooms = pd.DataFrame(rooms)
print("Rooms:\n", df_rooms.head(), "\n")

# ---- Parse times ----
time_rows = []
for line in sections.get("TIMES", []):
    matcher = re.match(r"^(?P<days>.+?)\s{2,}(?P<slots>.+)$", line)
    days = matcher.group("days").strip() if matcher else line
    slots = matcher.group("slots") if matcher else ""
    matches = re.findall(r"(\d{1,2}:\d{2})\s*\((\d+)hrs\)", slots)
    if matches:
        for start, dur in matches:
            time_rows.append({"days": days, "start_time": start, "duration_hours": int(dur)})
    else:
        time_rows.append({"days": days, "start_time": None, "duration_hours": None})
df_times = pd.DataFrame(time_rows)
print("Times:\n", df_times.head(), "\n")

# ---- Parse dates ----
df_dates = pd.DataFrame(sections.get("DATES", []), columns=["date_info"])
print("Dates:\n", df_dates.head(), "\n")

# ---- Room assignments ----
room_assignments = []
last_exam = None
for line in sections.get("ROOM ASSIGNMENTS", []):
    m = re.match(r"^(?P<exam>\S+)\s+(?P<assignment>.+)$", line)
    if m and re.match(r"^[A-Z0-9]", m.group("exam")):
        last_exam = m.group("exam").strip()
        room_assignments.append({"exam": last_exam, "assignment": m.group("assignment").strip()})
    elif last_exam:
        room_assignments.append({"exam": last_exam, "assignment": line.strip()})
df_room_assignments = pd.DataFrame(room_assignments)
print("Room assignments:\n", df_room_assignments.head(), "\n")

# ---- Coincidences (exams that should be scheduled together) ----
coincidences = []
for idx, line in enumerate(sections.get("COINCIDENCES", []), start=1):
    cleaned = re.sub(r"\(.*?\)", "", line)
    cleaned = cleaned.replace("{", " ").replace("}", " ").replace("&", " ")
    exams = [token.strip("\\/") for token in cleaned.split() if re.match(r"[A-Z0-9]", token)]
    if exams:
        coincidences.append({"group": idx, "exams": exams})
df_coincidences = pd.DataFrame(coincidences)
print("Coincidences:\n", df_coincidences.head(), "\n")

# ---- Earliness priorities ----
earliness = []
for line in sections.get("EARLINESS PRIORITY (1-100)", []):
    m = re.match(r"^(?P<exam>\S+)\s+(?P<priority>\d+)", line)
    if m:
        exam_code = m.group("exam").strip("\\/")
        earliness.append({"exam": exam_code, "priority": int(m.group("priority"))})
df_earliness = pd.DataFrame(earliness)
print("Earliness priorities:\n", df_earliness.head(), "\n")

# ---- Misc constraints (kept as free text) ----
df_misc = pd.DataFrame(sections.get("MISC", []), columns=["note"])
print("Misc constraints:\n", df_misc.head(), "\n")


# Optionally dump everything to CSV for Gurobi/optimization input.
output_dir = BASE_DIR / "out"
output_dir.mkdir(exist_ok=True)
df_students.to_csv(output_dir / "students.csv", index=False)
df_enrolments.to_csv(output_dir / "enrolments.csv", index=False)
df_exams.to_csv(output_dir / "exams.csv", index=False)
df_rooms.to_csv(output_dir / "rooms.csv", index=False)
df_times.to_csv(output_dir / "times.csv", index=False)
df_dates.to_csv(output_dir / "dates.csv", index=False)
df_room_assignments.to_csv(output_dir / "room_assignments.csv", index=False)
df_coincidences.to_csv(output_dir / "coincidences.csv", index=False)
df_earliness.to_csv(output_dir / "earliness.csv", index=False)
df_misc.to_csv(output_dir / "misc_constraints.csv", index=False)

print(f"Wrote CSVs to {output_dir}")
