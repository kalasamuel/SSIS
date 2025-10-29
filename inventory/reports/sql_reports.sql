-- Yearly
SELECT YEAR(sale_datetime) AS year,
       SUM(total_amount) AS total_sales,
       COUNT(*) AS transactions
FROM sale
GROUP BY YEAR(sale_datetime)
ORDER BY YEAR(sale_datetime);


-- Quarterly
SELECT YEAR(sale_datetime) AS sales_year,
       QUARTER(sale_datetime) AS sales_quarter,
       SUM(total_amount) AS total_sales,
       COUNT(*) AS transactions
FROM sale
GROUP BY sales_year, sales_quarter
ORDER BY sales_year, sales_quarter;
