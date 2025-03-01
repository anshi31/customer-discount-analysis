/*1.	Identify customers who haven't placed an order in the last 60 days but had at least 2 orders before.*/
SELECT customer_id
FROM orderss
WHERE STR_TO_DATE(order_date, '%d-%m-%Y') <= CURRENT_DATE - INTERVAL 60 DAY
GROUP BY customer_id
HAVING COUNT(order_id) >= 2;


/*2.	Calculate the average time between consecutive orders for repeated customers.*/
WITH ct AS (
    SELECT 
        customer_id, 
        order_id, 
        STR_TO_DATE(order_date, '%d-%m-%Y') AS formatted_odate,
        LAG(STR_TO_DATE(order_date, '%d-%m-%Y')) OVER (
            PARTITION BY customer_id 
            ORDER BY STR_TO_DATE(order_date, '%d-%m-%Y')
        ) AS prev_order_date
    FROM orderss
)
SELECT 
    customer_id, 
    order_id, 
    formatted_odate, 
    prev_order_date,
    DATEDIFF(formatted_odate, prev_order_date) AS days_between_orders
FROM ct;

/*3.	Determine the top 10% of customers by total spend and their average order value.*/
with cust_spend as (
select customer_id,
sum(total_amount) as total_spend,
count(order_id) as total_orders,
sum(total_amount)/ count(order_id) as avg_value_order
from orderss 
group by customer_id
),

 rank_cust as (
select *,
NTILE(10) over (order by total_spend desc) as percentile_rnk
from cust_spend
)
 select customer_id,total_spend,total_orders,avg_value_order
 from rank_cust 
 where percentile_rnk = 1;
	

/* 4. Analyze delivery time efficiency by calculating the percentage of on-time deliveries per region.*/
with cte as (
select o.city as region, count(*) as total_deliveries,
sum(case when dp.delivery_status = 'On Time' then 1 else 0 end) as on_time_deliveries
from orderss as o 
join delivery_performance as dp 
on o.order_id = dp.order_id 
group by city
)
select region,total_deliveries,on_time_deliveries,
concat(round((on_time_deliveries/total_deliveries)*100,2),'%')  as on_time_percentage
from cte

 









