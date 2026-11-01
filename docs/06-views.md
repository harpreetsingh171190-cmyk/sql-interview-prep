# Views

A view is a saved query that you can use like a table. It does not store data itself. Each time you select from the view, the database runs the saved query again. This page uses the sample tables from [SELECT basics](01-select-basics.md). Each example is self-contained.

## 1. What is a view?

A view hides a complex query behind a simple name. Other people can read the view without knowing the joins or filters inside it.

```sql
CREATE VIEW vw_EngineeringStaff AS
SELECT FirstName, LastName, Salary
FROM Employees
WHERE DepartmentId = 2;

SELECT * FROM vw_EngineeringStaff ORDER BY FirstName;
```

## 2. How do you combine tables in a view?

A view can contain joins. This view gives each employee's department name, so users do not need to write the join themselves.

```sql
CREATE VIEW vw_EmployeeDepartments AS
SELECT e.FirstName, e.LastName, d.DepartmentName
FROM Employees AS e
INNER JOIN Departments AS d ON d.DepartmentId = e.DepartmentId;

SELECT FirstName, DepartmentName FROM vw_EmployeeDepartments ORDER BY FirstName;
```

## 3. Does a view store data?

No. A standard view only saves the query. If the underlying table changes, the next select from the view shows the new data. This example shows that a view always reflects the current table.

```sql
CREATE VIEW vw_HighSalary AS
SELECT FirstName, Salary FROM Employees WHERE Salary >= 60000;

UPDATE Employees SET Salary = 65000 WHERE EmployeeId = 4;

SELECT FirstName, Salary FROM vw_HighSalary ORDER BY FirstName;
```

## 4. How do you remove a view?

Use `DROP VIEW`. Dropping a view does not delete any data from the tables it reads.

```sql
CREATE VIEW vw_Temp AS SELECT FirstName FROM Employees;
DROP VIEW vw_Temp;

SELECT COUNT(*) AS EmployeeCount FROM Employees;
```

## Note for SQL Server

SQL Server works the same way with `CREATE VIEW` and `DROP VIEW`. SQL Server also supports `WITH SCHEMABINDING` and indexed views, which store results. Those are more advanced topics and are not covered here.
