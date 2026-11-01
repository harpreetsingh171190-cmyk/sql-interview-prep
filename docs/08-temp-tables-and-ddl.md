# Temporary Tables and DDL

DDL (data definition language) changes the structure of the database, using `CREATE`, `ALTER`, and `DROP`. A temporary table holds data only while the session is open. This page uses the sample tables from [SELECT basics](01-select-basics.md). Each example is self-contained.

## 1. What is a temporary table?

A temporary table is useful for holding an intermediate result that you need for several steps. It disappears when the connection closes. In SQLite, use `CREATE TEMP TABLE`. In SQL Server, the same idea uses a name that starts with `#`, such as `#TopEarners`.

```sql
CREATE TEMP TABLE TopEarners AS
SELECT FirstName, Salary FROM Employees WHERE Salary > 60000;

SELECT FirstName, Salary FROM TopEarners ORDER BY Salary DESC;
```

## 2. How do you add a column to an existing table?

Use `ALTER TABLE ... ADD`. The new column is empty (`NULL`) for every existing row until you fill it in.

```sql
ALTER TABLE Employees ADD Email TEXT;

SELECT FirstName, Email FROM Employees ORDER BY EmployeeId;
```

## 3. How do you remove a table safely?

Use `DROP TABLE IF EXISTS`. The `IF EXISTS` part stops the statement from failing when the table is already gone.

```sql
DROP TABLE IF EXISTS StagingImport;

SELECT COUNT(*) AS EmployeeCount FROM Employees;
```

## 4. What is the difference between DELETE and TRUNCATE?

`DELETE` removes rows one at a time, can use a `WHERE` clause, and can be rolled back inside a transaction. `TRUNCATE` removes all rows quickly, but it has no `WHERE` clause. SQLite has no `TRUNCATE` statement, so the example uses `DELETE` with a condition.

```sql
DELETE FROM Employees WHERE EmployeeId = 5;

SELECT COUNT(*) AS EmployeeCount FROM Employees;
```

## Note for SQL Server

SQL Server supports `TRUNCATE TABLE Employees;`. Its temporary tables use the `#` prefix, and global temporary tables use `##`. Be careful with `TRUNCATE` on a table that other tables reference, because SQL Server does not allow it in that case.
