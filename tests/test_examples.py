"""Run the SQL examples in docs/ against a real SQLite database.

Only the standard library is used, so CI needs no installs.
"""

import re
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SQL_BLOCK = re.compile(r"```sql\n(.*?)```", re.DOTALL)


def extract_blocks(markdown: str) -> list[str]:
    return [block.strip() for block in SQL_BLOCK.findall(markdown)]


def all_blocks() -> list[tuple[str, str]]:
    found = []
    for path in sorted(DOCS.glob("*.md")):
        for block in extract_blocks(path.read_text(encoding="utf-8")):
            found.append((path.name, block))
    return found


def sample_schema() -> str:
    """The first SQL block in the SELECT page creates the sample tables."""
    page = (DOCS / "01-select-basics.md").read_text(encoding="utf-8")
    return extract_blocks(page)[0]


class SqlExamplesTest(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.executescript(sample_schema())

    def tearDown(self):
        self.conn.close()

    def query(self, sql: str):
        return [tuple(row) for row in self.conn.execute(sql).fetchall()]

    def test_docs_contain_sql_examples(self):
        self.assertGreater(len(all_blocks()), 5)

    def test_every_example_runs_without_error(self):
        for filename, block in all_blocks():
            if block.upper().startswith("CREATE TABLE"):
                continue  # the schema is already loaded in setUp
            with self.subTest(file=filename, sql=block[:40]):
                self.conn.execute(block.rstrip(";") + ";").fetchall()

    def test_null_check_finds_the_employee_without_department(self):
        rows = self.query("SELECT FirstName FROM Employees WHERE DepartmentId IS NULL;")
        self.assertEqual(rows, [("Priya",)])

    def test_group_by_counts_employees_per_department(self):
        rows = self.query(
            "SELECT DepartmentId, COUNT(*) FROM Employees "
            "WHERE DepartmentId IS NOT NULL GROUP BY DepartmentId ORDER BY DepartmentId;"
        )
        self.assertEqual(rows, [(1, 1), (2, 2), (3, 1)])

    def test_inner_join_leaves_out_employee_without_department(self):
        rows = self.query(
            "SELECT e.FirstName, d.DepartmentName FROM Employees AS e "
            "INNER JOIN Departments AS d ON d.DepartmentId = e.DepartmentId "
            "ORDER BY e.FirstName;"
        )
        names = [r[0] for r in rows]
        self.assertNotIn("Priya", names)
        self.assertEqual(len(rows), 4)

    def test_left_join_count_counts_matches_only(self):
        rows = self.query(
            "SELECT d.DepartmentName, COUNT(e.EmployeeId) FROM Departments AS d "
            "LEFT JOIN Employees AS e ON e.DepartmentId = d.DepartmentId "
            "GROUP BY d.DepartmentName ORDER BY d.DepartmentName;"
        )
        self.assertEqual(rows, [("Engineering", 2), ("HR", 1), ("Sales", 1)])

    def test_having_filters_groups_by_average(self):
        rows = self.query(
            "SELECT DepartmentId, AVG(Salary) FROM Employees WHERE DepartmentId IS NOT NULL "
            "GROUP BY DepartmentId HAVING AVG(Salary) > 50000 ORDER BY DepartmentId;"
        )
        self.assertEqual(rows, [(2, 70000.0), (3, 52000.0)])

    def test_scalar_subquery_finds_above_average_salaries(self):
        rows = self.query(
            "SELECT FirstName FROM Employees "
            "WHERE Salary > (SELECT AVG(Salary) FROM Employees) ORDER BY FirstName;"
        )
        self.assertEqual(rows, [("Meera",), ("Rahul",)])

    def test_exists_returns_departments_with_employees(self):
        rows = self.query(
            "SELECT d.DepartmentName FROM Departments AS d WHERE EXISTS "
            "(SELECT 1 FROM Employees AS e WHERE e.DepartmentId = d.DepartmentId) "
            "ORDER BY d.DepartmentName;"
        )
        self.assertEqual(rows, [("Engineering",), ("HR",), ("Sales",)])

    def test_case_assigns_salary_bands(self):
        rows = self.query(
            "SELECT FirstName, CASE WHEN Salary >= 60000 THEN 'High' "
            "WHEN Salary >= 45000 THEN 'Medium' ELSE 'Entry' END "
            "FROM Employees ORDER BY EmployeeId;"
        )
        self.assertEqual(rows, [
            ("Asha", "Medium"), ("Rahul", "High"), ("Meera", "High"),
            ("John", "Medium"), ("Priya", "Entry"),
        ])

    def test_distinct_and_like(self):
        ids = self.query(
            "SELECT DISTINCT DepartmentId FROM Employees "
            "WHERE DepartmentId IS NOT NULL ORDER BY DepartmentId;"
        )
        self.assertEqual(ids, [(1,), (2,), (3,)])
        names = self.query(
            "SELECT FirstName FROM Employees WHERE LastName LIKE 'S%' ORDER BY FirstName;"
        )
        self.assertEqual(names, [("John",), ("Rahul",)])


if __name__ == "__main__":
    unittest.main()
