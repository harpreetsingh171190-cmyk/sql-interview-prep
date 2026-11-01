# Transactions and Stored Procedures

A transaction groups several changes so they succeed or fail together. This page uses the sample tables from [SELECT basics](01-select-basics.md). Each SQL example is self-contained.

## 1. What is a transaction?

A transaction is a set of statements that the database treats as one unit. If any step fails, you can undo all of them with `ROLLBACK`. If everything is fine, you save them with `COMMIT`.

```sql
BEGIN TRANSACTION;
UPDATE Employees SET Salary = Salary + 1000 WHERE EmployeeId = 1;
ROLLBACK;

SELECT FirstName, Salary FROM Employees WHERE EmployeeId = 1;
```

## 2. How do you save changes with COMMIT?

Use `COMMIT` when every step in the transaction is correct. After `COMMIT`, the changes are permanent.

```sql
BEGIN TRANSACTION;
UPDATE Employees SET Salary = Salary + 1000 WHERE EmployeeId = 1;
COMMIT;

SELECT FirstName, Salary FROM Employees WHERE EmployeeId = 1;
```

## 3. What is a stored procedure?

A stored procedure is a named piece of T-SQL saved on the server. It can take parameters and run several statements. This example is written for SQL Server, so it is shown in a `tsql` block and is not run in CI, because SQLite does not support stored procedures.

```tsql
CREATE PROCEDURE GetEmployeesByDepartment
    @DepartmentId INT
AS
BEGIN
    SELECT FirstName, LastName
    FROM Employees
    WHERE DepartmentId = @DepartmentId;
END;

EXEC GetEmployeesByDepartment @DepartmentId = 2;
```

## 4. How do you handle errors inside a transaction in SQL Server?

Use `TRY...CATCH`. If an error happens in the `TRY` block, the `CATCH` block runs, and you can roll back the transaction there. This is also shown as `tsql`, because it is SQL Server syntax.

```tsql
BEGIN TRY
    BEGIN TRANSACTION;
    UPDATE Employees SET Salary = Salary + 1000 WHERE EmployeeId = 1;
    COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
    THROW;
END CATCH;
```

## Note for SQL Server

SQL Server uses `BEGIN TRANSACTION` and `COMMIT TRANSACTION`, and `ROLLBACK` works the same as shown above. Stored procedures are the main tool for reusable logic on the server.
