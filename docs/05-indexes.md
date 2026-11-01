# Indexes

An index is a separate structure that helps the database find rows quickly, the same way the index at the back of a book helps you find a page. This page uses the sample tables from [SELECT basics](01-select-basics.md). Each example is self-contained, so you can run it on its own.

## 1. What does an index do?

Without an index, the database checks every row to find matches. This is called a table scan. An index lets it jump straight to the matching rows, but it costs extra storage, and every insert, update, or delete must also update the index.

## 2. How do you create an index?

Use `CREATE INDEX` on the column you search or join on often. This example creates an index and then uses it in a filtered query.

```sql
CREATE INDEX IX_Employees_DepartmentId ON Employees (DepartmentId);

SELECT FirstName FROM Employees WHERE DepartmentId = 2 ORDER BY FirstName;
```

## 3. Why does the column order matter in a composite index?

A composite index covers more than one column. It works best for searches on the first column, or on the first column plus the second. A search on the second column alone usually cannot use it well.

```sql
CREATE INDEX IX_Employees_Dept_Salary ON Employees (DepartmentId, Salary);

SELECT FirstName, Salary FROM Employees
WHERE DepartmentId = 2 AND Salary > 60000
ORDER BY Salary DESC;
```

## 4. What is a unique index?

A unique index stops two rows from having the same value in that column. It works like a primary key rule, but you can add it to any column.

```sql
CREATE UNIQUE INDEX UX_Departments_Name ON Departments (DepartmentName);

SELECT DepartmentName FROM Departments ORDER BY DepartmentName;
```

## 5. How do you remove an index?

Use `DROP INDEX`. This example creates an index, removes it, and then checks that the query still works without it.

```sql
CREATE INDEX IX_Temp_Salary ON Employees (Salary);
DROP INDEX IX_Temp_Salary;

SELECT COUNT(*) AS EmployeeCount FROM Employees;
```

## 6. When should you not add an index?

Avoid indexes on small tables, on columns that change often, and on columns with very few distinct values, such as a yes or no flag. Each index slows down writes and uses more space. Check the query plan before and after you add one.

## Note for SQL Server

SQL Server requires a name and table in the drop statement, for example `DROP INDEX IX_Temp_Salary ON Employees;`. It also supports `CREATE CLUSTERED INDEX` and `CREATE NONCLUSTERED INDEX`. The examples above use SQLite syntax so they can be tested in CI.
