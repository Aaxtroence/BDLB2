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

    def to_line(self):
        return f"{self.last}, {self.first}, {self.grade}, {self.classroom}, {self.bus}\n"

class Teacher:
    def __init__(self, last, first, classroom):
        self.last = last.strip()
        self.first = first.strip()
        self.classroom = classroom.strip()

    def __repr__(self):
        return f"{self.last}, {self.first}, {self.classroom}"

    def to_line(self):
        return f"{self.last}, {self.first}, {self.classroom}\n"

def get_file_path(filename):
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, filename)
    dirpath = os.path.dirname(path)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath, exist_ok=True)
    if not os.path.exists(path):
        open(path, "a", encoding="utf-8").close()
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
        idx["by_last"].setdefault(s.last.upper(), []).append(s)
        idx["by_bus"].setdefault(s.bus, []).append(s)
        idx["by_class"].setdefault(s.classroom, []).append(s)
        idx["by_grade"].setdefault(s.grade, []).append(s)

    if teachers:
        for t in teachers:
            idx["teachers_by_class"].setdefault(t.classroom, []).append(t)

    return idx

def save_students_file(students):
    path = get_file_path("list.txt")
    with open(path, "w", encoding="utf-8") as f:
        for s in students:
            f.write(s.to_line())
    print(f"Збережено {len(students)} учнів у list.txt")

def save_teachers_file(teachers):
    path = get_file_path("teachers.txt")
    with open(path, "w", encoding="utf-8") as f:
        for t in teachers:
            f.write(t.to_line())
    print(f"Збережено {len(teachers)} викладачів у teachers.txt")

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
    for s in idx["by_last"].get(last.upper(), []):
        teachers = idx["teachers_by_class"].get(s.classroom, [])
        if teachers:
            for t in teachers:
                res.append(f"{s.last}, {s.first}, {s.grade}, {s.classroom}, {s.bus}, {t.last}, {t.first}")
        else:
            res.append(f"{s.last}, {s.first}, {s.grade}, {s.classroom}, {s.bus}")
    return res

def find_student_bus(last, idx):
    res = []
    for s in idx["by_last"].get(last.upper(), []):
        res.append(f"{s.last}, {s.first}, Bus: {s.bus}")
    return res

def find_teacher_students(last, idx):
    res = []
    target = last.upper()
    for class_id, teachers in idx["teachers_by_class"].items():
        for t in teachers:
            if t.last.upper() == target:
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
    for g in sorted(grade_stats.keys(), key=lambda x: (not x.isdigit(), x)):
        print(f"Grade {g}: {grade_stats[g]} учнів")

def add_student(students, teachers, idx):
    last = input("Прізвище: ").strip()
    first = input("Ім'я: ").strip()
    grade = input("Grade: ").strip()
    classroom = input("Classroom: ").strip()
    bus = input("Bus: ").strip()

    new_s = Student(last, first, grade, classroom, bus)
    students.append(new_s)

    idx["by_last"].setdefault(new_s.last.upper(), []).append(new_s)
    idx["by_bus"].setdefault(new_s.bus, []).append(new_s)
    idx["by_class"].setdefault(new_s.classroom, []).append(new_s)
    idx["by_grade"].setdefault(new_s.grade, []).append(new_s)

    save_students_file(students)
    print("Студента додано.")

def add_teacher(teachers, idx):
    last = input("Прізвище: ").strip()
    first = input("Ім'я: ").strip()
    classroom = input("Classroom: ").strip()

    new_t = Teacher(last, first, classroom)
    teachers.append(new_t)

    idx["teachers_by_class"].setdefault(new_t.classroom, []).append(new_t)

    save_teachers_file(teachers)
    print("Викладача додано.")

def delete_student(students, teachers, idx, last, first=None):
    """Видаляє студента по прізвищу або прізвищу+імені. Повертає кількість видалених."""
    last_u = last.upper()
    first_u = first.upper() if first else None
    removed_count = 0
    new_list = []
    for s in students:
        if s.last.upper() == last_u and (first_u is None or s.first.upper() == first_u):
            removed_count += 1
            continue
        new_list.append(s)
    if removed_count == 0:
        print("Студента не знайдено.")
        return 0
    students[:] = new_list
    new_idx = build_indexes(students, teachers)
    idx.clear()
    idx.update(new_idx)
    save_students_file(students)
    print(f"Видалено {removed_count} студента(ів).")
    return removed_count

def update_student(students, teachers, idx, last, first=None):
    """Оновити першого знайденого студента за прізвищем (і опційно іменем)."""
    last_u = last.upper()
    first_u = first.upper() if first else None
    target = None
    for s in students:
        if s.last.upper() == last_u and (first_u is None or s.first.upper() == first_u):
            target = s
            break
    if not target:
        print("Не знайдено студента для оновлення.")
        return False

    print("Залиш поле порожнім, щоб зберегти поточне значення.")
    new_last = input(f"Прізвище [{target.last}]: ").strip() or target.last
    new_first = input(f"Ім'я [{target.first}]: ").strip() or target.first
    new_grade = input(f"Grade [{target.grade}]: ").strip() or target.grade
    new_class = input(f"Classroom [{target.classroom}]: ").strip() or target.classroom
    new_bus = input(f"Bus [{target.bus}]: ").strip() or target.bus

    target.last = new_last
    target.first = new_first
    target.grade = new_grade
    target.classroom = new_class
    target.bus = new_bus

    new_idx = build_indexes(students, teachers)
    idx.clear()
    idx.update(new_idx)
    save_students_file(students)
    print("Дані студента оновлено.")
    return True

def print_help():
    print("\nДоступні команди:")
    print("S[tudent]: <lastname>              - Пошук студента за прізвищем")
    print("S[tudent]: <lastname> B[us]        - Пошук автобусного маршруту студента")
    print("T[eacher]: <lastname>              - Пошук студентів викладача")
    print("B[us]: <number>                    - Пошук студентів за автобусним маршрутом")
    print("G[rade]: <number>                  - Пошук студентів за рівнем класу")
    print("C[lassroom]: <number>              - Пошук студентів за класом")
    print("C[lassroom]: <number> T[eacher]    - Пошук викладачів класу")
    print("G[rade]: <number> T[eacher]        - Пошук викладачів за grade")
    print("")
    print("A[dd] S[tudent]                     - Додати нового студента")
    print("A[dd] T[eacher]                     - Додати нового викладача")
    print("D[elete] S[tudent] <lastname> [first] - Видалити студента (можна вказати ім'я для точності)")
    print("U[pdate] S[tudent] <lastname> [first] - Оновити дані студента (вкажи ім'я для точності)")
    print("")
    print("STAT[S]                             - Показати статистику")
    print("SAVE J[SON]                         - Зберегти дані у JSON")
    print("SAVE X[ML]                          - Зберегти дані у XML")
    print("H[elp]                              - Показати довідку")
    print("Q[uit]                              - Вийти з програми\n")

def parse_name_args(parts, start_index=1):
    """Допоміжна: повертає (lastname, firstname_or_None) з частин команди."""
    if len(parts) <= start_index:
        return None, None
    last = parts[start_index]
    first = parts[start_index + 1] if len(parts) > start_index + 1 else None
    return last, first

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
                print("До побачення!")
                break

            elif c in ["H", "HELP"]:
                print_help()

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
                    print("SAVE J[SON] або SAVE X[ML].")

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
                else:
                    print("Вкажіть номер автобуса.")

            elif c.startswith("G"):
                if len(parts) >= 2:
                    grade = parts[1]
                    if len(parts) >= 3 and parts[2].upper().startswith("T"):
                        res, t = measure_time(find_grade_teachers, grade, idx)
                    else:
                        res, t = measure_time(find_grade, grade, idx)
                    print_list(res)
                    print(f"{t}ms")
                else:
                    print("Вкажіть grade.")

            elif c.startswith("C"):
                if len(parts) >= 2:
                    classroom = parts[1]
                    if len(parts) >= 3 and parts[2].upper().startswith("T"):
                        res, t = measure_time(find_classroom_teachers, classroom, idx)
                    else:
                        res, t = measure_time(find_classroom_students, classroom, idx)
                    print_list(res)
                    print(f"{t}ms")
                else:
                    print("Вкажіть classroom.")

            elif c in ["A", "ADD"]:
                if len(parts) >= 2 and parts[1].upper().startswith("S"):
                    add_student(students, teachers, idx)
                elif len(parts) >= 2 and parts[1].upper().startswith("T"):
                    add_teacher(teachers, idx)
                else:
                    print("ADD S[tudent] або ADD T[eacher]")

            elif c in ["D", "DELETE"]:
                if len(parts) >= 3 and parts[1].upper().startswith("S"):
                    last, first = parse_name_args(parts, 2)
                    delete_student(students, teachers, idx, last, first)
                else:
                    print("DELETE S[tudent] <lastname> [first]")

            elif c in ["U", "UPDATE"]:
                if len(parts) >= 3 and parts[1].upper().startswith("S"):
                    last, first = parse_name_args(parts, 2)
                    update_student(students, teachers, idx, last, first)
                else:
                    print("UPDATE S[tudent] <lastname> [first]")

            else:
                print("Невідома команда. (HELP для списку)")

        except KeyboardInterrupt:
            print("\nПрограму перервано. До побачення!")
            break
        except Exception as e:
            print(f"Помилка: {e}")

if __name__ == "__main__":
    main()
