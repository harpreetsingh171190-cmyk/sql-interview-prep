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
