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
                self.conn.execute("SELECT 1")  # connection still usable
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


if __name__ == "__main__":
    unittest.main()
