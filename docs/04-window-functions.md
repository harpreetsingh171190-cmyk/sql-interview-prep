# Window Functions

This page continues from [subqueries and CTEs](03-subqueries-and-ctes.md). It uses the same sample tables, so run the schema from [SELECT basics](01-select-basics.md) first.

## 1. What is a window function?

A window function calculates a value for each row by looking at a set of related rows, called a window. Unlike `GROUP BY`, it does not combine rows, so every employee still appears in the result. The `OVER` clause defines the window.

```sql
SELECT FirstName, Salary,
       AVG(Salary) OVER () AS CompanyAverage
FROM Employees
ORDER BY EmployeeId;
```

## 2. How do you number rows inside each department?

`ROW_NUMBER()` gives each row a number. `PARTITION BY` splits the rows into groups, and `ORDER BY` sets the order inside each group. The `WHERE` clause removes employees with no department, so they are not numbered.

```sql
SELECT FirstName, DepartmentId, Salary,
       ROW_NUMBER() OVER (PARTITION BY DepartmentId ORDER BY Salary DESC) AS RowNum
FROM Employees
WHERE DepartmentId IS NOT NULL
ORDER BY DepartmentId, RowNum;
```

## 3. What is the difference between RANK and DENSE_RANK?

When two rows tie, `RANK` leaves a gap in the numbers after them, while `DENSE_RANK` does not. The example uses a small derived table so you can see the tie without changing the sample data.

```sql
SELECT Name, Score,
       RANK() OVER (ORDER BY Score DESC) AS RankNo,
       DENSE_RANK() OVER (ORDER BY Score DESC) AS DenseRankNo
FROM (
    SELECT 'Asha' AS Name, 90 AS Score
    UNION ALL
    SELECT 'Rahul', 90
    UNION ALL
    SELECT 'Meera', 80
) AS Scores
ORDER BY Score DESC, Name;
```

## 4. How do you calculate a running total?

Add `ORDER BY` inside `OVER`. Each row then sums its own value and all the rows before it.

```sql
SELECT FirstName, Salary,
       SUM(Salary) OVER (ORDER BY EmployeeId) AS RunningTotal
FROM Employees
ORDER BY EmployeeId;
```

## 5. How do you compare a row with the previous row?

`LAG` returns a value from an earlier row. The first row has no previous row, so it returns `NULL`.

```sql
SELECT FirstName, Salary,
       LAG(Salary) OVER (ORDER BY EmployeeId) AS PreviousSalary
FROM Employees
ORDER BY EmployeeId;
```

## 6. How do you find the top earner in each department?

Number the rows inside each department, then keep only number 1. Window functions cannot be used in `WHERE` directly, so put the numbering in a CTE first.

```sql
WITH Ranked AS (
    SELECT FirstName, DepartmentId, Salary,
           ROW_NUMBER() OVER (PARTITION BY DepartmentId ORDER BY Salary DESC) AS RowNum
    FROM Employees
    WHERE DepartmentId IS NOT NULL
)
SELECT FirstName, DepartmentId, Salary
FROM Ranked
WHERE RowNum = 1
ORDER BY DepartmentId;
```

## Note for SQL Server

Window functions work the same way in SQL Server and SQLite. The derived table in item 3 uses `UNION ALL` instead of `VALUES`, so it runs in both. One difference to remember: SQLite treats `NULL` as the smallest value when sorting, while SQL Server treats it as the smallest too, so the results in these examples match.
