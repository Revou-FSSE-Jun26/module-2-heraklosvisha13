-- =========================================================================
-- Example SQL Queries with case WHERE, ORDER BY, and LIMIT clauses
-- =========================================================================

-- 1. Find all products under 1000000, order by cheapest, limit to 5
SELECT * 
FROM products 
WHERE price < 1000000 
ORDER BY price ASC 
LIMIT 5;

-- 2. Find all orders for user with id=1 (e.g., Budi)
SELECT * 
FROM orders 
WHERE user_id = 1;