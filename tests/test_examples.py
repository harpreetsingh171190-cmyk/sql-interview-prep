"""Run the SQL examples in docs/ against a real SQLite database.

Only the standard library is used, so CI needs no installs.
Each example runs on a fresh copy of the sample schema, so blocks
cannot affect one another.
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


def fresh_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(sample_schema())
    return conn


class SqlExamplesTest(unittest.TestCase):
    def setUp(self):
        self.conn = fresh_db()

    def tearDown(self):
        self.conn.close()

    def query(self, sql: str, conn=None):
        conn = conn or self.conn
        return [tuple(row) for row in conn.execute(sql).fetchall()]

    def test_docs_contain_sql_examples(self):
        self.assertGreater(len(all_blocks()), 20)

    def test_every_example_runs_without_error(self):
        for filename, block in all_blocks():
            if block.upper().startswith("CREATE TABLE"):
                continue  # the schema is already loaded by fresh_db()
            with self.subTest(file=filename, sql=block[:40]):
                conn = fresh_db()
                try:
                    conn.executescript(block)
                finally:
                    conn.close()

    # Chapter 1: SELECT basics
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
        self.assertNotIn("Priya", [r[0] for r in rows])
        self.assertEqual(len(rows), 4)

    # Chapter 2: joins and grouping
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

    # Chapter 3: subqueries and CTEs
    def test_cte_filters_engineering_staff(self):
        rows = self.query(
            "WITH EngineeringStaff AS (SELECT FirstName, Salary FROM Employees "
            "WHERE DepartmentId = 2) SELECT FirstName, Salary FROM EngineeringStaff "
            "ORDER BY Salary DESC;"
        )
        self.assertEqual(rows, [("Rahul", 72000), ("Meera", 68000)])

    def test_multiple_ctes_total_salary_per_department(self):
        rows = self.query(
            "WITH DeptTotals AS (SELECT DepartmentId, SUM(Salary) AS TotalSalary "
            "FROM Employees WHERE DepartmentId IS NOT NULL GROUP BY DepartmentId) "
            "SELECT d.DepartmentName, t.TotalSalary FROM DeptTotals AS t "
            "INNER JOIN Departments AS d ON d.DepartmentId = t.DepartmentId "
            "ORDER BY d.DepartmentName;"
        )
        self.assertEqual(rows, [("Engineering", 140000), ("HR", 52000), ("Sales", 45000)])

    def test_derived_table_filters_group_averages(self):
        rows = self.query(
            "SELECT t.DepartmentId, t.AvgSalary FROM (SELECT DepartmentId, AVG(Salary) "
            "AS AvgSalary FROM Employees WHERE DepartmentId IS NOT NULL "
            "GROUP BY DepartmentId) AS t WHERE t.AvgSalary > 50000 "
            "ORDER BY t.DepartmentId;"
        )
        self.assertEqual(rows, [(2, 70000.0), (3, 52000.0)])

    def test_not_in_with_null_returns_no_rows(self):
        rows = self.query(
            "SELECT DepartmentName FROM Departments "
            "WHERE DepartmentId NOT IN (SELECT DepartmentId FROM Employees);"
        )
        self.assertEqual(rows, [])

    def test_recursive_cte_counts_to_five(self):
        rows = self.query(
            "WITH RECURSIVE Numbers(n) AS (SELECT 1 UNION ALL "
            "SELECT n + 1 FROM Numbers WHERE n < 5) SELECT n FROM Numbers;"
        )
        self.assertEqual(rows, [(1,), (2,), (3,), (4,), (5,)])

    # Chapter 4: window functions
    def test_row_number_numbers_employees_per_department(self):
        rows = self.query(
            "SELECT FirstName, DepartmentId, Salary, "
            "ROW_NUMBER() OVER (PARTITION BY DepartmentId ORDER BY Salary DESC) AS RowNum "
            "FROM Employees WHERE DepartmentId IS NOT NULL ORDER BY DepartmentId, RowNum;"
        )
        self.assertEqual(rows, [
            ("Asha", 1, 45000, 1),
            ("Rahul", 2, 72000, 1),
            ("Meera", 2, 68000, 2),
            ("John", 3, 52000, 1),
        ])

    def test_rank_leaves_gap_and_dense_rank_does_not(self):
        rows = self.query(
            "SELECT Name, Score, RANK() OVER (ORDER BY Score DESC), "
            "DENSE_RANK() OVER (ORDER BY Score DESC) FROM ("
            "SELECT 'Asha' AS Name, 90 AS Score UNION ALL "
            "SELECT 'Rahul', 90 UNION ALL SELECT 'Meera', 80) AS Scores "
            "ORDER BY Score DESC, Name;"
        )
        self.assertEqual(rows, [("Asha", 90, 1, 1), ("Rahul", 90, 1, 1), ("Meera", 80, 3, 2)])

    def test_running_total_adds_each_row(self):
        rows = self.query(
            "SELECT SUM(Salary) OVER (ORDER BY EmployeeId) FROM Employees ORDER BY EmployeeId;"
        )
        self.assertEqual(rows, [(45000,), (117000,), (185000,), (237000,), (276000,)])

    def test_lag_returns_previous_salary_and_null_for_first_row(self):
        rows = self.query(
            "SELECT FirstName, LAG(Salary) OVER (ORDER BY EmployeeId) "
            "FROM Employees ORDER BY EmployeeId;"
        )
        self.assertEqual(rows, [
            ("Asha", None), ("Rahul", 45000), ("Meera", 72000),
            ("John", 68000), ("Priya", 52000),
        ])

    def test_top_earner_per_department(self):
        rows = self.query(
            "WITH Ranked AS (SELECT FirstName, DepartmentId, Salary, "
            "ROW_NUMBER() OVER (PARTITION BY DepartmentId ORDER BY Salary DESC) AS RowNum "
            "FROM Employees WHERE DepartmentId IS NOT NULL) "
            "SELECT FirstName, DepartmentId, Salary FROM Ranked WHERE RowNum = 1 "
            "ORDER BY DepartmentId;"
        )
        self.assertEqual(rows, [("Asha", 1, 45000), ("Rahul", 2, 72000), ("John", 3, 52000)])

    # Chapter 5: indexes
    def test_index_is_created_and_used_by_name(self):
        self.conn.execute("CREATE INDEX IX_Employees_DepartmentId ON Employees (DepartmentId);")
        names = self.query(
            "SELECT name FROM sqlite_master WHERE type = 'index' "
            "AND name = 'IX_Employees_DepartmentId';"
        )
        self.assertEqual(names, [("IX_Employees_DepartmentId",)])

    def test_unique_index_rejects_duplicate_department_name(self):
        self.conn.execute("CREATE UNIQUE INDEX UX_Departments_Name ON Departments (DepartmentName);")
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute("INSERT INTO Departments VALUES (4, 'Sales');")

    def test_index_example_returns_engineering_names(self):
        conn = fresh_db()
        try:
            conn.executescript(
                "CREATE INDEX IX_Employees_DepartmentId ON Employees (DepartmentId);"
            )
            rows = self.query(
                "SELECT FirstName FROM Employees WHERE DepartmentId = 2 ORDER BY FirstName;",
                conn=conn,
            )
            self.assertEqual(rows, [("Meera",), ("Rahul",)])
        finally:
            conn.close()

    # Chapter 6: views
    def test_view_returns_engineering_staff(self):
        self.conn.execute(
            "CREATE VIEW vw_EngineeringStaff AS SELECT FirstName, LastName, Salary "
            "FROM Employees WHERE DepartmentId = 2;"
        )
        rows = self.query("SELECT FirstName FROM vw_EngineeringStaff ORDER BY FirstName;")
        self.assertEqual(rows, [("Meera",), ("Rahul",)])

    def test_view_reflects_table_changes(self):
        self.conn.execute(
            "CREATE VIEW vw_HighSalary AS SELECT FirstName, Salary FROM Employees "
            "WHERE Salary >= 60000;"
        )
        self.conn.execute("UPDATE Employees SET Salary = 65000 WHERE EmployeeId = 4;")
        rows = self.query("SELECT FirstName FROM vw_HighSalary ORDER BY FirstName;")
        self.assertEqual(rows, [("John",), ("Meera",), ("Rahul",)])

    # Chapter 7: transactions
    def test_rollback_undoes_the_salary_change(self):
        conn = fresh_db()
        try:
            conn.executescript(
                "BEGIN TRANSACTION; "
                "UPDATE Employees SET Salary = Salary + 1000 WHERE EmployeeId = 1; "
                "ROLLBACK;"
            )
            rows = self.query("SELECT Salary FROM Employees WHERE EmployeeId = 1;", conn=conn)
            self.assertEqual(rows, [(45000,)])
        finally:
            conn.close()

    def test_commit_keeps_the_salary_change(self):
        conn = fresh_db()
        try:
            conn.executescript(
                "BEGIN TRANSACTION; "
                "UPDATE Employees SET Salary = Salary + 1000 WHERE EmployeeId = 1; "
                "COMMIT;"
            )
            rows = self.query("SELECT Salary FROM Employees WHERE EmployeeId = 1;", conn=conn)
            self.assertEqual(rows, [(46000,)])
        finally:
            conn.close()

    # Chapter 8: temporary tables and DDL
    def test_temp_table_holds_only_high_earners(self):
        conn = fresh_db()
        try:
            conn.executescript(
                "CREATE TEMP TABLE TopEarners AS "
                "SELECT FirstName, Salary FROM Employees WHERE Salary > 60000;"
            )
            rows = self.query(
                "SELECT FirstName FROM TopEarners ORDER BY FirstName;", conn=conn
            )
            self.assertEqual(rows, [("Meera",), ("Rahul",)])
        finally:
            conn.close()

    def test_alter_table_adds_empty_column(self):
        self.conn.execute("ALTER TABLE Employees ADD Email TEXT;")
        rows = self.query("SELECT Email FROM Employees ORDER BY EmployeeId;")
        self.assertEqual(rows, [(None,)] * 5)

    def test_delete_removes_one_employee(self):
        self.conn.execute("DELETE FROM Employees WHERE EmployeeId = 5;")
        rows = self.query("SELECT COUNT(*) FROM Employees;")
        self.assertEqual(rows, [(4,)])


if __name__ == "__main__":
    unittest.main()
