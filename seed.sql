-- ===============================
-- Sample Data 
-- ===============================

-- 1. Insert sample data into categories
INSERT INTO categories (category_name) VALUES
('Electronics'),
('Accessories'),
('Books'),
('Clothing');

-- 2. Insert sample data into users
INSERT INTO users (name, email) VALUES
('Budi Santoso', 'budi@example.com'),
('Siti Aminah', 'siti@example.com'),
('Andi Wijaya', 'andi@example.com'),
('Dewi Lestari', 'dewi@example.com');

-- 3. Insert sample data into products
INSERT INTO products (name, price, stock, category_id) VALUES
('Laptop Lenovo ThinkPad', 12000000, 10, 1),
('Smartphone Samsung Galaxy', 8000000, 15, 1),
('Wireless Mouse Logitech', 250000, 50, 2),
('Mechanical Keyboard Razer', 1500000, 20, 2),
('Novel Filosofi Kopi', 85000, 100, 3),
('T-Shirt Uniqlo', 120000, 200, 4),
('Jeans Levi’s', 450000, 80, 4);

--- 4. Insert sample data into orders
INSERT INTO orders (user_id, total_price, status) VALUES
(1, 8500000, 'completed'),   -- Budi beli Galaxy + Mouse
(2, 12000000, 'pending'),    -- Siti beli Laptop
(3, 535000, 'completed');    -- Andi beli Jeans + Novel

--- 5. Insert sample data into order_items
-- Order 1: Budi
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(1, 2, 1, 8000000),   -- Samsung Galaxy
(1, 3, 2, 250000);    -- 2x Mouse

-- Order 2: Siti
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(2, 1, 1, 12000000);  -- Laptop Lenovo

-- Order 3: Andi
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(3, 7, 1, 450000),    -- Jeans Levi’s
(3, 5, 1, 85000);     -- Novel Filosofi Kopi

