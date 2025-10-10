//Raw SQL — yearly

SELECT YEAR(sale_datetime) AS year,
       SUM(total_amount) AS total_sales,
       COUNT(*) AS transactions
FROM sales
GROUP BY YEAR(sale_datetime)
ORDER BY YEAR(sale_datetime);

//Raw SQL — quarterly

SELECT CONCAT(YEAR(sale_datetime), '-Q', QUARTER(sale_datetime)) AS period,
       SUM(total_amount) AS total_sales,
       COUNT(*) AS transactions
FROM sales
GROUP BY YEAR(sale_datetime), QUARTER(sale_datetime)
ORDER BY YEAR(sale_datetime), QUARTER(sale_datetime);
