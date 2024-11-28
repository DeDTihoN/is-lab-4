from typing import List, Dict, Callable, Any, Tuple


def select_unassigned_variable(assignments, variables, constraints, domains):
    """
    Вибирає змінну за допомогою degree heuristic (змінна з найбільшою кількістю обмежень).
    """
    unassigned_vars = [v for v in variables if v not in {k for a in assignments for k in a}]
    # Підрахунок кількості обмежень для кожної змінної
    def degree(var):
        return sum(1 for constraint in constraints if var in constraint["vars"])
    # Вибираємо змінну з найбільшим ступенем
    return max(unassigned_vars, key=degree)

def order_domain_values(var, domains, assignments, constraints):
    """
    Впорядковує значення для змінної за принципом least constraining value.
    """
    def count_conflicts(value):
        # Підрахунок кількості конфліктів для цього значення
        test_assignment = {var: value}
        return sum(
            not constraint["predicate"](assignments + [test_assignment], *[
                test_assignment.get(v) for v in constraint["vars"]
            ])
            for constraint in constraints if var in constraint["vars"]
        )
    # Сортуємо значення за кількістю конфліктів
    return sorted(domains[var], key=count_conflicts)


class CSP:
    def __init__(self, variables, domains, constraints):
        self.variables = variables  # Список змінних
        self.domains = domains  # Області визначення для кожної змінної
        self.constraints = constraints  # Список обмежень
        self.assignments = []  # Поточний розклад (список подій)

    def is_consistent(self, new_assignment):
        """
        Перевіряє, чи нова подія відповідає всім обмеженням.
        """
        for constraint in self.constraints:
            vars_in_constraint = constraint["vars"]
            relevant_assignments = [
                a for a in self.assignments + [new_assignment] if all(var in a for var in vars_in_constraint)
            ]
            for assignment in relevant_assignments:
                values = [assignment[var] for var in vars_in_constraint]
                if not constraint["predicate"](self.assignments + [new_assignment], *values):
                    return False
        return True

    def backtracking_search(self):
        """
        Генерує повний розклад.
        """
        # Якщо всі змінні заповнені, повертаємо розклад
        if len(self.assignments) == CNT_LECTURES * len(self.domains["group"]):
            return self.assignments

        # Вибираємо змінну для присвоєння
        for group in self.domains["group"]:
            for time in self.domains["time"]:
                for lecturer in self.domains["lecturer"]:
                    for classroom in self.domains["classroom"]:
                        new_assignment = {
                            "group": group,
                            "time": time,
                            "lecturer": lecturer,
                            "classroom": classroom,
                        }
                        # Перевіряємо, чи присвоєння не порушує обмеження
                        if self.is_consistent(new_assignment):
                            # Додаємо подію до розкладу
                            self.assignments.append(new_assignment)

                            # Рекурсивний виклик
                            result = self.backtracking_search()
                            if result is not None:
                                return result

                            # Відкат
                            self.assignments.pop()

        # Якщо не вдалося знайти рішення, повертаємо None
        return None


# Змінні
variables = ["lecturer", "classroom", "group", "time"]

# Області визначення
domains = {
    "lecturer": ["lecturer 1", "lecturer 2", "lecturer 3", "lecturer 4"],
    "time": ["Monday 9:00", "Monday 11:00", "Tuesday 9:00", "Tuesday 11:00"],
    "classroom": ["Auditorium 101", "Auditorium 102", "Auditorium 103"],
    "group": ["Group 1", "Group 2", "Group 3"],
}

CNT_LECTURES = 3

# Обмеження
constraints = [
    # Викладач не може проводити більше однієї лекції одночасно.
    {
        "vars": ("lecturer", "time"),
        "predicate": lambda events, l, t: sum(
            e["lecturer"] == l and e["time"] == t for e in events
        ) <= 1,
    },
    # Група не може бути присутньою на кількох лекціях одночасно.
    {
        "vars": ("group", "time"),
        "predicate": lambda events, g, t: sum(
            e["group"] == g and e["time"] == t for e in events
        ) <= 1,
    },
    # Аудиторія не може використовуватись для кількох лекцій одночасно.
    {
        "vars": ("classroom", "time"),
        "predicate": lambda events, r, t: sum(
            e["classroom"] == r and e["time"] == t for e in events
        ) <= 1,
    },
    # Часові обмеження для викладачів.
    {
        "vars": ("lecturer", "time"),
        "predicate": lambda events, l, t: (l, t) in [
            ("lecturer 1", "Monday 9:00"),
            ("lecturer 1", "Monday 11:00"),
            ("lecturer 1", "Tuesday 11:00"),
            ("lecturer 2", "Monday 9:00"),
            ("lecturer 2", "Monday 11:00"),
            ("lecturer 2", "Tuesday 9:00"),
            ("lecturer 2", "Tuesday 11:00"),
            ("lecturer 3", "Monday 9:00"),
            ("lecturer 3", "Monday 11:00"),
            ("lecturer 3", "Tuesday 9:00"),
            ("lecturer 3", "Tuesday 11:00"),
            ("lecturer 4", "Tuesday 9:00"),
        ],
    },
    # Обмеження на кількість пар для кожної групи.
    {
        "vars": ("group",),
        "predicate": lambda events, g: sum(
            e["group"] == g for e in events
        ) <= CNT_LECTURES,
    }
]

# Ініціалізація CSP
csp = CSP(variables, domains, constraints)

# Генерація розкладу
solution = csp.backtracking_search()

if solution:
    print("Розклад знайдено:")
    for assignment in solution:
        print(assignment)
else:
    print("Розклад не знайдено.")
