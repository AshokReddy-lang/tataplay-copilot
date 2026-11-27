-- sql queries

-- Q1 --->>> Revenue by plan

SELECT p.plan_name,
       SUM(r.amount_inr)   AS revenue_inr,
       ROUND(AVG(r.amount_inr),2)  AS avg_revenue_air,
       COUNT(DISTINCT r.subscriber_id) AS subscribers
FROM recharges r
INNER JOIN subscribers s ON s.subscriber_id =r.subscriber_id
INNER JOIN plans p ON p.plan_id=s.plan_id
WHERE r.status= "success"
GROUP BY p.plan_name
ORDER BY revenue_inr DESC;

--Q2  --->>>  subscribers who never successfully recharged
SELECT s.subscriber_id, s.tenure_months, s.plan_id, s.city
FROM subscribers s
LEFT JOIN (SELECT * FROM recharges WHERE status = 'success') r
       ON r.subscriber_id = s.subscriber_id
WHERE r.recharge_id IS NULL
ORDER BY s.subscriber_id;

--Q3  --->>>  ranking with in a city
WITH totals AS (
    SELECT s.subscriber_id, s.city, SUM(r.amount_inr) AS total_inr
    FROM subscribers s
    INNER JOIN recharges r ON r.subscriber_id = s.subscriber_id
    WHERE r.status = 'success'
    GROUP BY s.subscriber_id, s.city
)
SELECT city, subscriber_id, total_inr,
       RANK()       OVER (PARTITION BY city ORDER BY total_inr DESC)                AS rnk,
       DENSE_RANK() OVER (PARTITION BY city ORDER BY total_inr DESC)                AS dense_rnk,
       ROW_NUMBER() OVER (PARTITION BY city ORDER BY total_inr DESC, subscriber_id) AS row_num
FROM totals
ORDER BY city, row_num;

--Q4  --->>> Running totals for subscriber TP00010
SELECT recharge_id, recharge_date, amount_inr,
       SUM(amount_inr) OVER (ORDER BY recharge_date, recharge_id) AS running_total_inr
FROM recharges
WHERE subscriber_id = 'TP00010' AND status = 'success'
ORDER BY recharge_date, recharge_id;