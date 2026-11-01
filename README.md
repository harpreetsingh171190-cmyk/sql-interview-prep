# SQL Server Interview Prep

Short, practical notes for SQL Server interviews. Every example is written in plain SQL and tested against a real database in continuous integration (CI), so the code on each page is known to run.

## What is inside

| Topic | Status |
|-------|--------|
| [SELECT basics](docs/01-select-basics.md) (filtering, sorting, NULL, GROUP BY, joins) | Ready |
| Joins in depth | Planned |
| Indexes | Planned |
| Views and stored procedures | Planned |

## Why the examples are tested

Interview answers are only useful if the code is correct. The tests in [`tests/`](tests/) run every SQL example against SQLite, a small database that is built into Python. SQL Server syntax differs in a few places (for example `TOP` instead of `LIMIT`), and each page notes those differences.

## Running the tests

No installation is needed. Python 3.12 or newer is enough.

```bash
python -m unittest discover -s tests -v
```

## Project layout

```
docs/     the study pages, one topic per file
tests/    checks that run every SQL example
.github/  CI workflow
```

## License

Apache 2.0. See [LICENSE](LICENSE).
