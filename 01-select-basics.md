# SELECT Basics

This page covers the first queries most SQL Server interviews start with. Each example runs on the sample tables below, so you can check the results yourself.

## Sample tables

```sql
CREATE TABLE Departments (
    DepartmentId INTEGER PRIMARY KEY,
    DepartmentName TEXT NOT NULL
);

CREATE TABLE Employees (
    EmployeeId INTEGER PRIMARY KEY,
    FirstName TEXT NOT NULL,
    LastName TEXT NOT NULL,
    DepartmentId INTEGER,
    Salary INTEGER
);

INSERT INTO Departments VALUES (1, 'Sales'), (2, 'Engineering'), (3, 'HR');

INSERT INTO Employees VALUES
    (1, 'Asha', 'Kaur', 1, 45000),
    (2, 'Rahul', 'Singh', 2, 72000),
    (3, 'Meera', 'Patel', 2, 68000),
    (4, 'John', 'Smith', 3, 52000),
    (5, 'Priya', 'Verma', NULL, 39000);
```

## 1. How do you get all columns from a table?

Use `SELECT *`. It is quick for exploring data, but in real work it is better to list the columns you need.

```sql
SELECT * FROM Employees;
```

## 2. How do you get only some columns?

List the column names after `SELECT`, separated by commas.

```sql
SELECT FirstName, LastName FROM Employees;
```

## 3. How do you filter rows?

Use `WHERE`. It keeps only the rows where the condition is true.

```sql
SELECT FirstName, Salary FROM Employees WHERE Salary > 50000;
```

## 4. How do you sort the results?

Use `ORDER BY`. Add `DESC` to sort from highest to lowest.

```sql
SELECT FirstName, Salary FROM Employees ORDER BY Salary DESC;
```

## 5. How do you find rows with no department?

Use `IS NULL`. Do not write `= NULL`, because that comparison never returns true.

```sql
SELECT FirstName FROM Employees WHERE DepartmentId IS NULL;
```

## 6. How do you count rows in each group?

Use `GROUP BY` with `COUNT`.

```sql
SELECT DepartmentId, COUNT(*) AS EmployeeCount
FROM Employees
WHERE DepartmentId IS NOT NULL
GROUP BY DepartmentId
ORDER BY DepartmentId;
```

## 7. How do you join two tables?

An `INNER JOIN` returns only the rows that match in both tables.

```sql
SELECT e.FirstName, d.DepartmentName
FROM Employees AS e
INNER JOIN Departments AS d ON d.DepartmentId = e.DepartmentId
ORDER BY e.FirstName;
```

## Note for SQL Server

SQL Server uses `TOP` to limit rows, for example `SELECT TOP 3 * FROM Employees;`. SQLite, used here for testing, uses `LIMIT 3` instead. The examples on this page avoid `TOP` so they run on both.
