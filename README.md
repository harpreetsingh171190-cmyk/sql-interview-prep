# SQL Server Interview Prep

Practical notes for SQL Server interviews, in eight short chapters. Every SQL example that uses plain SQL is run against a real database in continuous integration (CI), so the code on each page is known to work.

## Chapters

| # | Topic | Questions |
|---|-------|-----------|
| 1 | [SELECT basics](docs/01-select-basics.md) | 7 |
| 2 | [Joins and grouping](docs/02-joins-and-grouping.md) | 7 |
| 3 | [Subqueries and CTEs](docs/03-subqueries-and-ctes.md) | 5 |
| 4 | [Window functions](docs/04-window-functions.md) | 6 |
| 5 | [Indexes](docs/05-indexes.md) | 6 |
| 6 | [Views](docs/06-views.md) | 4 |
| 7 | [Transactions and stored procedures](docs/07-transactions-and-procedures.md) | 4 |
| 8 | [Temporary tables and DDL](docs/08-temp-tables-and-ddl.md) | 4 |

## How the examples are checked

The tests in [`tests/`](tests/) run each SQL example against SQLite, a small database built into Python. Each example starts from a fresh copy of the sample tables. SQL Server differs from SQLite in a few places, such as `TOP` instead of `LIMIT`. Those differences are noted on each page.

Examples written only for SQL Server, such as stored procedures and `TRY...CATCH`, use a `tsql` code block. They are shown for reading and are not run, because SQLite cannot execute them.

## Running the tests

No installation is needed. Python 3.12 or newer is enough.

```bash
python -m unittest discover -s tests -v
```

## Project layout

```
docs/     one study page per chapter
tests/    checks that run the SQL examples
.github/  CI workflow
```

## License

Apache 2.0. See [LICENSE](LICENSE).
