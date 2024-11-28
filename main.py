import random
from constraint import Problem, AllDifferentConstraint

# Ініціалізація проблеми
problem = Problem()

# Генерація вхідних даних
groups = [f"G{i+1}" for i in range(3)]  # Генеруємо 3 групи
lecturers = [f"L{i+1}" for i in range(3)]  # Генеруємо 3 лекторів
subjects = ["Math", "Physics", "Chemistry"]  # Предмети
rooms = [f"R{i+1}" for i in range(3)]  # Генеруємо 3 аудиторії
slots = [(day, time) for day in range(5) for time in range(4)]  # 5 днів по 4 слоти

# Генерація розмірів групи
group_sizes = {group: random.randint(10, 30) for group in groups}  # Розмір кожної групи

# Генерація предметів для кожної групи
group_subjects = {group: random.sample(subjects, k=random.randint(1, len(subjects))) for group in groups}

# Генерація аудиторій з їхньою вмістимістю
room_capacity = {room: random.randint(20, 40) for room in rooms}

# Генерація лекторів з їхніми предметами та типами занять
lecturer_subjects = {
    lecturer: {
        "subjects": random.sample(subjects, k=random.randint(1, len(subjects))),
        "types": random.choices(["lecture", "practice", "both"], k=len(subjects))
    }
    for lecturer in lecturers
}

# Генерація підгруп для кожної групи
group_subgroups = {group: [f"{group}_sub{i+1}" for i in range(2)] for group in groups}

# Генерація кількості годин для кожного предмету
subject_hours = {
    subject: {"lecture": random.randint(10, 20), "practice": random.randint(5, 15)}
    for subject in subjects
}

# Ініціалізація змінних для обліку проведених лекцій та практик
subject_schedule = {
    group: {
        subject: {"lecture": 0, "practice": 0} for subject in group_subjects[group]
    }
    for group in groups
}

# Додавання змінних (групи, підгрупи, лекції, аудиторії, часові слоти)
for group in groups:
    problem.addVariable(group, slots)
for subgroup in [sub for subs in group_subgroups.values() for sub in subs]:
    problem.addVariable(subgroup, slots)
for lecturer in lecturers:
    problem.addVariable(lecturer, slots)
for room in rooms:
    problem.addVariable(room, slots)

# Додавання обмежень
# Жорстке обмеження: одна група може мати лише одне заняття в один період часу
def no_conflict(*args):
    return len(set(args)) == len(args)

# Групи не можуть мати заняття в один і той самий час
problem.addConstraint(no_conflict, groups)
# Підгрупи не можуть мати заняття в один і той самий час
problem.addConstraint(no_conflict, [sub for subs in group_subgroups.values() for sub in subs])
# Лектори не можуть викладати одночасно в різних місцях
problem.addConstraint(no_conflict, lecturers)
# Аудиторії не можуть використовуватися для кількох занять одночасно
problem.addConstraint(no_conflict, rooms)

# Додавання обмежень на аудиторії (вмістимість)
def room_capacity_constraint(group, room):
    return group_sizes[group] <= room_capacity[room]

for group in groups:
    for room in rooms:
        problem.addConstraint(room_capacity_constraint, (group, room))

# Додавання обмежень на лекторів і предмети
def lecturer_subject_constraint(group, lecturer):
    subjects_for_group = group_subjects[group]
    subjects_for_lecturer = lecturer_subjects[lecturer]["subjects"]
    return any(subject in subjects_for_lecturer for subject in subjects_for_group)

for group in groups:
    for lecturer in lecturers:
        problem.addConstraint(lecturer_subject_constraint, (group, lecturer))

# Додавання обмеження для практичних занять на підгрупах
def practice_constraint(subgroup, lecturer):
    group = subgroup.split("_sub")[0]
    subjects_for_group = group_subjects[group]
    subjects_for_lecturer = lecturer_subjects[lecturer]["subjects"]
    types_for_lecturer = lecturer_subjects[lecturer]["types"]
    return any(subject in subjects_for_lecturer and types_for_lecturer[subjects.index(subject)] in ["practice", "both"] for subject in subjects_for_group)

for subgroup in [sub for subs in group_subgroups.values() for sub in subs]:
    for lecturer in lecturers:
        problem.addConstraint(practice_constraint, (subgroup, lecturer))

# Додавання обмеження для лекцій у одній аудиторії для кількох груп
def shared_lecture_constraint(group1, group2, lecturer, room):
    return lecturer_subject_constraint(group1, lecturer) and lecturer_subject_constraint(group2, lecturer) and room_capacity[room] >= (group_sizes[group1] + group_sizes[group2])

problem.addConstraint(shared_lecture_constraint, ("G1", "G2", "L1", "R1"))

# Додавання обмеження на кількість годин занять для кожного предмету
def subject_hours_constraint(group, subject, lecture_slot, practice_slot):
    if lecture_slot:
        subject_schedule[group][subject]["lecture"] += 1
    if practice_slot:
        subject_schedule[group][subject]["practice"] += 1
    required_lecture_hours = subject_hours[subject]["lecture"]
    required_practice_hours = subject_hours[subject]["practice"]
    return subject_schedule[group][subject]["lecture"] <= required_lecture_hours and subject_schedule[group][subject]["practice"] <= required_practice_hours

for group in groups:
    for subject in group_subjects[group]:
        for slot in slots:
            lecture_slot = random.choice([True, False])  # Змінна для визначення, чи є слот лекцією
            practice_slot = random.choice([True, False])  # Змінна для визначення, чи є слот практикою
            problem.addConstraint(subject_hours_constraint, (group, subject, lecture_slot, practice_slot))

# Додавання інших обмежень (наприклад, щоб було менше "вікон" у розкладі)
def minimize_gaps(*args):
    # Мінімізувати кількість "вікон" у розкладі
    return True

problem.addConstraint(minimize_gaps, groups + lecturers)

# Пошук рішення
solution = problem.getSolution()

# Вивід розкладу
if solution:
    for group in groups:
        print(f"Група {group}: слот {solution[group]}")
    for subgroup in [sub for subs in group_subgroups.values() for sub in subs]:
        print(f"Підгрупа {subgroup}: слот {solution[subgroup]}")
    for lecturer in lecturers:
        print(f"Викладач {lecturer}: слот {solution[lecturer]}")
    for room in rooms:
        print(f"Аудиторія {room}: слот {solution[room]}")
else:
    print("Розв'язок не знайдено")