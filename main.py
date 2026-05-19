# STEP 0

# SQL Library and Pandas Library
import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('data.sqlite')

pd.read_sql("""SELECT * FROM sqlite_master""", conn)

# STEP 1
# Return the first and last names and the job titles for all employees in Boston
df_boston = pd.read_sql("""
    SELECT e.firstName, e.lastName
    FROM employees AS e
    JOIN offices AS o ON e.officeCode = o.officeCode
    WHERE o.city = 'Boston';
""", conn)

# STEP 2
# Are there any offices that have zero employees?
df_zero_emp = pd.read_sql("""
    SELECT o.officeCode, o.city
    FROM offices AS o
    LEFT JOIN employees AS e ON o.officeCode = e.officeCode
    WHERE e.officeCode IS NULL;
""", conn)

# STEP 3
# Return the employees' first name and last name, along with the city and state of the office that they work out of (if they have one). Include all employees and order them by their first name, then their last name
df_employee = pd.read_sql("""
    SELECT e.firstName, e.lastName, o.city, o.state
    FROM employees AS e
    LEFT JOIN offices AS o ON e.officeCode = o.officeCode
    ORDER BY e.firstName ASC, e.lastName ASC;
""", conn)

# STEP 4
# Return all of the customer's contact information (first name, last name, and phone number) as well as their sales rep's employee number for any customer who has not placed an order

# Sort the results alphabetically based on the contact's last name. There are several approaches you could take here, including a left join and filtering on null values or using a subquery to filter out customers who do have orders. In total, 24 customers have not placed an order
df_contacts = pd.read_sql("""
    SELECT contactFirstName, contactLastName, phone, salesRepEmployeeNumber
    FROM customers 
    WHERE customerNumber NOT IN (
        SELECT DISTINCT customerNumber
        FROM orders
        WHERE customerNumber IS NOT NULL
    )
    ORDER BY contactLastName ASC;
""", conn)

# STEP 5
# produce a report of all the customer contacts (first and last names) along with details for each of the customers' payment amounts and dates of payment

# results be sorted in descending order by the payment amount
df_payment = pd.read_sql("""
    SELECT 
        c.contactFirstName, 
        c.contactLastName, 
        p.amount, 
        p.paymentDate
    FROM customers AS c
    JOIN payments AS p ON c.customerNumber = p.customerNumber
    ORDER BY CAST(p.amount AS FLOAT) DESC;
""", conn)

# STEP 6
# Return the employee number, first name, last name, and number of customers for employees whose customers have an average credit limit over 90k

# Sort by number of customers from high to low.
df_credit = pd.read_sql("""
    SELECT 
        e.employeeNumber, 
        e.firstName, 
        e.lastName, 
        COUNT(c.customerNumber) AS number_of_customers
    FROM employees AS e
    JOIN customers AS c ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY e.employeeNumber, e.firstName, e.lastName
    HAVING AVG(c.creditLimit) > 90000
    ORDER BY number_of_customers DESC;
""", conn)

# STEP 7
# Return the product name and count the number of orders for each product as a column named numorders

# Also return a new column, totalunits, that sums up the total quantity of product sold (use the quantityOrdered column)

# Sort the results by the totalunits column, highest to lowest, to showcase the top-selling products
df_product_sold = pd.read_sql("""
    SELECT 
        p.productName,
        COUNT(od.orderNumber) AS numorders, 
        SUM(od.quantityOrdered) AS totalunits
    FROM products AS p
    JOIN orderdetails AS od ON p.productCode = od.productCode
    GROUP BY p.productCode, p.productName
    ORDER BY totalunits DESC;
""", conn)

# STEP 8
# Return the product name, code, and the total number of customers who have ordered each product, aliased as numpurchasers

# Sort the results by the highest number of purchasers
df_total_customers = pd.read_sql("""
    SELECT
        p.productName, 
        p.productCode,  -- <-- Added the missing comma here
        COUNT(DISTINCT o.customerNumber) AS numpurchasers
    FROM products AS p
    JOIN orderdetails AS od ON p.productCode = od.productCode
    JOIN orders AS o ON od.orderNumber = o.orderNumber
    GROUP BY p.productCode, p.productName
    ORDER BY numpurchasers DESC; 
""", conn)

# STEP 9
# Return the count as a column named n_customers

# return the office code and city
df_customers = pd.read_sql("""
    SELECT 
        COUNT(c.customerNumber) AS n_customers, 
        ofc.officeCode,
        ofc.city
    FROM offices AS ofc
    JOIN employees AS e ON ofc.officeCode = e.officeCode
    JOIN customers AS c ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY ofc.officeCode, ofc.city;
""", conn)

# STEP 10
# subquery or common table expression (CTE), select the employee number, first name, last name, city of the office, and the office code for employees who sold products that have been ordered by fewer than 20 customers
df_under_20 = pd.read_sql("""
    SELECT DISTINCT
        e.employeeNumber,
        e.firstName,
        e.lastName,
        ofc.city,
        ofc.officeCode
    FROM employees AS e
    JOIN offices AS ofc ON e.officeCode = ofc.officeCode
    JOIN customers AS c ON e.employeeNumber = c.salesRepEmployeeNumber
    JOIN orders AS o ON c.customerNumber = o.customerNumber
    JOIN orderdetails AS od ON o.orderNumber = od.orderNumber
    WHERE od.productCode IN (
        SELECT od_sub.productCode
        FROM orderdetails AS od_sub
        JOIN orders AS o_sub ON od_sub.orderNumber = o_sub.orderNumber
        GROUP BY od_sub.productCode
        HAVING COUNT(DISTINCT o_sub.customerNumber) < 20
    )
    ORDER BY e.lastName ASC, e.firstName DESC;
""", conn)

# Close the connection
conn.close()