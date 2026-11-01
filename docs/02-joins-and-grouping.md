# Joins, Grouping and Subqueries

This page builds on [SELECT basics](01-select-basics.md). It uses the same sample tables, so run the schema from that page first.

## 1. What is the difference between INNER JOIN and LEFT JOIN?

An `INNER JOIN` keeps only rows that match on both sides. A `LEFT JOIN` keeps every row from the left table, and fills the right-side columns with `NULL` when there is no match.

```sql
SELECT d.DepartmentName, e.FirstName
FROM Departments AS d
LEFT JOIN Employees AS e ON e.DepartmentId = d.DepartmentId
ORDER BY d.DepartmentName, e.FirstName;
```

## 2. Why use COUNT(column) instead of COUNT(*) after a LEFT JOIN?

`COUNT(*)` counts every row, including the rows where the right side is `NULL`. `COUNT(e.EmployeeId)` counts only the rows that actually matched. This is a common interview trap.

```sql
SELECT d.DepartmentName, COUNT(e.EmployeeId) AS EmployeeCount
FROM Departments AS d
LEFT JOIN Employees AS e ON e.DepartmentId = d.DepartmentId
GROUP BY d.DepartmentName
ORDER BY d.DepartmentName;
```

## 3. What is the difference between WHERE and HAVING?

`WHERE` filters rows before grouping. `HAVING` filters groups after `GROUP BY` has been applied, so it is the place for conditions on aggregates such as `AVG`.

```sql
SELECT DepartmentId, AVG(Salary) AS AvgSalary
FROM Employees
WHERE DepartmentId IS NOT NULL
GROUP BY DepartmentId
HAVING AVG(Salary) > 50000
ORDER BY DepartmentId;
```

## 4. How do you compare a row with an aggregate value?

Put the aggregate query inside brackets. This is called a scalar subquery, because it returns one value.

```sql
SELECT FirstName
FROM Employees
WHERE Salary > (SELECT AVG(Salary) FROM Employees)
ORDER BY FirstName;
```

## 5. How do you find departments that have at least one employee?

Use `EXISTS`. It returns true as soon as the inner query finds one matching row, which makes it efficient for this kind of check.

```sql
SELECT d.DepartmentName
FROM Departments AS d
WHERE EXISTS (
    SELECT 1
    FROM Employees AS e
    WHERE e.DepartmentId = d.DepartmentId
)
ORDER BY d.DepartmentName;
```

## 6. How do you group values into bands?

Use `CASE` to create a new column with a label for each row. The first matching `WHEN` wins, and `ELSE` handles everything else.

```sql
SELECT FirstName,
       CASE
           WHEN Salary >= 60000 THEN 'High'
           WHEN Salary >= 45000 THEN 'Medium'
           ELSE 'Entry'
       END AS SalaryBand
FROM Employees
ORDER BY EmployeeId;
```

## 7. How do you remove duplicates and match a text pattern?

`DISTINCT` removes repeated values. `LIKE` matches text, and `%` means any number of characters.

```sql
SELECT DISTINCT DepartmentId
FROM Employees
WHERE DepartmentId IS NOT NULL
ORDER BY DepartmentId;
```

```sql
SELECT FirstName
FROM Employees
WHERE LastName LIKE 'S%'
ORDER BY FirstName;
```

## Note for SQL Server

Both queries in item 7 and all the joins above work the same way in SQL Server. The difference to remember is that SQL Server uses `TOP` where SQLite uses `LIMIT`, and this page does not use either.
