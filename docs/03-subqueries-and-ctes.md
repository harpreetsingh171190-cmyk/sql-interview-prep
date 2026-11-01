# Subqueries and Common Table Expressions (CTEs)

This page continues from [joins and grouping](02-joins-and-grouping.md). It uses the same sample tables, so run the schema from [SELECT basics](01-select-basics.md) first.

## 1. What is a CTE?

A common table expression (CTE) is a named result set that you define with `WITH`. It exists only for the one query that follows it. CTEs make long queries easier to read, because each step has a name.

```sql
WITH EngineeringStaff AS (
    SELECT FirstName, Salary
    FROM Employees
    WHERE DepartmentId = 2
)
SELECT FirstName, Salary
FROM EngineeringStaff
ORDER BY Salary DESC;
```

## 2. How do you use more than one CTE?

Separate the CTEs with commas. A later CTE can use an earlier one, and the final query can join them.

```sql
WITH DeptTotals AS (
    SELECT DepartmentId, SUM(Salary) AS TotalSalary
    FROM Employees
    WHERE DepartmentId IS NOT NULL
    GROUP BY DepartmentId
)
SELECT d.DepartmentName, t.TotalSalary
FROM DeptTotals AS t
INNER JOIN Departments AS d ON d.DepartmentId = t.DepartmentId
ORDER BY d.DepartmentName;
```

## 3. What is a derived table?

A derived table is a subquery in the `FROM` clause. It works like a CTE, but it is written inline and has an alias. Use it when you need to filter the result of a group.

```sql
SELECT t.DepartmentId, t.AvgSalary
FROM (
    SELECT DepartmentId, AVG(Salary) AS AvgSalary
    FROM Employees
    WHERE DepartmentId IS NOT NULL
    GROUP BY DepartmentId
) AS t
WHERE t.AvgSalary > 50000
ORDER BY t.DepartmentId;
```

## 4. Why can NOT IN return no rows?

If the list from the subquery contains even one `NULL`, `NOT IN` cannot decide whether a value is missing from the list, so the result is empty. Priya has no department, so her `NULL` is in the list. This is a common interview trap.

```sql
SELECT DepartmentName
FROM Departments
WHERE DepartmentId NOT IN (SELECT DepartmentId FROM Employees);
```

To avoid the trap, remove the `NULL` values inside the subquery:

```sql
SELECT DepartmentName
FROM Departments
WHERE DepartmentId NOT IN (
    SELECT DepartmentId FROM Employees WHERE DepartmentId IS NOT NULL
);
```

## 5. How do you write a recursive CTE?

A recursive CTE refers to itself. It has an anchor part, which gives the first row, and a recursive part, which adds rows until the condition stops it. This example counts from 1 to 5.

```sql
WITH RECURSIVE Numbers(n) AS (
    SELECT 1
    UNION ALL
    SELECT n + 1 FROM Numbers WHERE n < 5
)
SELECT n FROM Numbers;
```

## Note for SQL Server

SQL Server does not use the word `RECURSIVE`. A recursive CTE there starts with `WITH Numbers(n) AS (...)`. The rest of the syntax is the same, so the examples on this page work in SQL Server after removing `RECURSIVE` from item 5.
