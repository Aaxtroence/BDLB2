import time
import json
import xml.etree.ElementTree as ET
import os
import sys
from datetime import datetime

class Student:
    def __init__(self, last, first, grade, classroom, bus):
        self.last = last.strip()
        self.first = first.strip()
        self.grade = grade.strip()
        self.classroom = classroom.strip()
        self.bus = bus.strip()

    def __repr__(self):
        return f"{self.last}, {self.first}, {self.grade}, {self.classroom}, {self.bus}"

class Teacher:
    def __init__(self, last, first, classroom):
        self.last = last.strip()
        self.first = first.strip()
        self.classroom = classroom.strip()

    def __repr__(self):
        return f"{self.last}, {self.first}, {self.classroom}"

def get_file_path(filename):
    """Повертає абсолютний шлях до файлу у папці з програмою"""
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, filename)
    if not os.path.exists(path):
        print(f"Помилка: файл '{filename}' не знайдено за шляхом {path}")
        sys.exit(1)
    return path

def load_students():
    path = get_file_path("list.txt")
    students = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = [x.strip() for x in line.split(",")]
            if len(parts) != 5:
                continue
            students.append(Student(*parts))
    print(f"Завантажено {len(students)} учнів із list.txt")
    return students

def load_teachers():
    path = get_file_path("teachers.txt")
    teachers = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = [x.strip() for x in line.split(",")]
            if len(parts) != 3:
                continue
            teachers.append(Teacher(*parts))
    print(f"Завантажено {len(teachers)} викладачів із teachers.txt")
    return teachers

def build_indexes(students, teachers):
    idx = {
        "by_last": {},
        "by_bus": {},
        "by_class": {},
        "by_grade": {},
        "teachers_by_class": {}
    }

    for s in students:
        idx["by_last"].setdefault(s.last, []).append(s)
        idx["by_bus"].setdefault(s.bus, []).append(s)
        idx["by_class"].setdefault(s.classroom, []).append(s)
        idx["by_grade"].setdefault(s.grade, []).append(s)

    for t in teachers:
        idx["teachers_by_class"].setdefault(t.classroom, []).append(t)

    return idx

def measure_time(func, *args):
    start = time.perf_counter()
    result = func(*args)
    end = time.perf_counter()
    return result, int((end - start) * 1000)

def print_list(lines):
    if lines:
        for line in lines:
            print(line)
    else:
        print("Нічого не знайдено.")

def find_student(last, idx):
    res = []
    for s in idx["by_last"].get(last, []):
        teachers = idx["teachers_by_class"].get(s.classroom, [])
        if teachers:
            for t in teachers:
                res.append(f"{s.last}, {s.first}, {s.grade}, {s.classroom}, {s.bus}, {t.last}, {t.first}")
        else:
            res.append(f"{s.last}, {s.first}, {s.grade}, {s.classroom}, {s.bus}")
    return res

def find_student_bus(last, idx):
    res = []
    for s in idx["by_last"].get(last, []):
        res.append(f"{s.last}, {s.first}, Bus: {s.bus}")
    return res

def find_teacher_students(last, idx):
    res = []
    for class_id, teachers in idx["teachers_by_class"].items():
        for t in teachers:
            if t.last.upper() == last.upper():
                for s in idx["by_class"].get(class_id, []):
                    res.append(f"{s.last}, {s.first}")
    return res

def find_bus(bus, idx):
    res = []
    for s in idx["by_bus"].get(bus, []):
        res.append(f"{s.last}, {s.first}, {s.grade}, {s.classroom}")
    return res

def find_grade(grade, idx):
    res = []
    for s in idx["by_grade"].get(grade, []):
        res.append(f"{s.last}, {s.first}")
    return res

def find_classroom_students(classroom, idx):
    res = []
    for s in idx["by_class"].get(classroom, []):
        res.append(f"{s.last}, {s.first}")
    return res

def find_classroom_teachers(classroom, idx):
    res = []
    for t in idx["teachers_by_class"].get(classroom, []):
        res.append(f"{t.last}, {t.first}, {t.classroom}")
    return res

def find_grade_teachers(grade, idx):
    found = set()
    for s in idx["by_grade"].get(grade, []):
        for t in idx["teachers_by_class"].get(s.classroom, []):
            found.add((t.last, t.first, t.classroom))
    return [f"{t[0]}, {t[1]}, {t[2]}" for t in sorted(found)]

def save_to_json(students, teachers):
    data = {
        "students": [s.__dict__ for s in students],
        "teachers": [t.__dict__ for t in teachers],
        "export_time": datetime.now().isoformat()
    }
    path = get_file_path("school_data.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Дані збережено у school_data.json")

def save_to_xml(students, teachers):
    root = ET.Element("school")
    students_el = ET.SubElement(root, "students")
    for s in students:
        st_el = ET.SubElement(students_el, "student")
        for k, v in s.__dict__.items():
            ET.SubElement(st_el, k).text = v
    teachers_el = ET.SubElement(root, "teachers")
    for t in teachers:
        te_el = ET.SubElement(teachers_el, "teacher")
        for k, v in t.__dict__.items():
            ET.SubElement(te_el, k).text = v
    ET.SubElement(root, "export_time").text = datetime.now().isoformat()
    tree = ET.ElementTree(root)
    tree.write(get_file_path("school_data.xml"), encoding="utf-8", xml_declaration=True)
    print("Дані збережено у school_data.xml")

def show_statistics(students):
    print(f"Загальна кількість студентів: {len(students)}")
    grade_stats = {}
    for s in students:
        grade_stats[s.grade] = grade_stats.get(s.grade, 0) + 1
    for g, c in grade_stats.items():
        print(f"Grade {g}: {c} учнів")

def print_help():
    print("\nДоступні команди:")
    print("S[tudent]: <lastname>          - Пошук студента за прізвищем")
    print("S[tudent]: <lastname> B[us]    - Пошук автобусного маршруту студента")
    print("T[eacher]: <lastname>          - Пошук студентів викладача")
    print("B[us]: <number>                - Пошук студентів за автобусним маршрутом")
    print("G[rade]: <number>              - Пошук студентів за рівнем класу")
    print("C[lassroom]: <number>          - Пошук студентів за класом")
    print("C[lassroom]: <number> T[eacher]- Пошук викладачів класу (нове)")
    print("G[rade]: <number> T[eacher]    - Пошук викладачів за grade (нове)")
    print("STAT[S]                        - Показати статистику")
    print("SAVE J[SON]                    - Зберегти дані у JSON")
    print("SAVE X[ML]                     - Зберегти дані у XML")
    print("H[elp]                         - Показати довідку")
    print("Q[uit]                         - Вийти з програми\n")

def main():
    students = load_students()
    teachers = load_teachers()
    idx = build_indexes(students, teachers)
    print_help()

    while True:
        cmd = input("\n> ").strip()
        if not cmd:
            continue
        parts = cmd.split()
        c = parts[0].upper()

        try:
            if c in ["Q", "QUIT"]:
                print("Quit bye!")
                break

            elif c in ["H", "HELP"]:
                print_help()

            elif c in ["STAT", "STATS"]:
                show_statistics(students)

            elif c.startswith("S"):
                if len(parts) >= 2:
                    last = parts[1]
                    if len(parts) >= 3 and parts[2].upper().startswith("B"):
                        res, t = measure_time(find_student_bus, last, idx)
                    else:
                        res, t = measure_time(find_student, last, idx)
                    print_list(res)
                    print(f"{t}ms")
                else:
                    print("Вкажіть прізвище студента.")

            elif c.startswith("T"):
                if len(parts) >= 2:
                    last = parts[1]
                    res, t = measure_time(find_teacher_students, last, idx)
                    print_list(res)
                    print(f"{t}ms")
                else:
                    print("Вкажіть прізвище викладача.")

            elif c.startswith("B"):
                if len(parts) >= 2:
                    res, t = measure_time(find_bus, parts[1], idx)
                    print_list(res)
                    print(f"{t}ms")

            elif c.startswith("G"):
                if len(parts) >= 2:
                    grade = parts[1]
                    if len(parts) >= 3 and parts[2].upper().startswith("T"):
                        res, t = measure_time(find_grade_teachers, grade, idx)
                    else:
                        res, t = measure_time(find_grade, grade, idx)
                    print_list(res)
                    print(f"{t}ms")

            elif c.startswith("C"):
                if len(parts) >= 2:
                    classroom = parts[1]
                    if len(parts) >= 3 and parts[2].upper().startswith("T"):
                        res, t = measure_time(find_classroom_teachers, classroom, idx)
                    else:
                        res, t = measure_time(find_classroom_students, classroom, idx)
                    print_list(res)
                    print(f"{t}ms")

            elif c in ["SAVE"]:
                if len(parts) >= 2:
                    fmt = parts[1].upper()
                    if fmt in ["J", "JSON"]:
                        save_to_json(students, teachers)
                    elif fmt in ["X", "XML"]:
                        save_to_xml(students, teachers)
                    else:
                        print("Вкажіть формат J[SON] або X[ML].")

            else:
                print("Невідома команда. (HELP для списку)")
        except Exception as e:
            print(f"Помилка: {e}")

if __name__ == "__main__":
    main()