-- =============================================
-- ENTITY MAP:
-- ---------------------------------------------
-- categories (1) ---> products (M)
-- users (1) ---> orders (M)
-- orders (M) ---> products (M)
-- =============================================

-- 1. Create table categories [Independent entity]
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(255) NOT NULL UNIQUE
);

-- 2. Create table users [Independent entity]
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT now()
);

-- 3. Create table products [Dependent entity]
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price numeric(10, 2) NOT NULL check (price >= 0),
    stock INT NOT NULL DEFAULT 0 check (stock >= 0),
    category_id INT,
    constraint fk_product_category foreign key (category_id) references categories(id) on delete set null
);

-- 4. Create table orders [Dependent entity]
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    total_price numeric(10, 2) NOT NULL check (total_price >= 0),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT now(),
    constraint fk_order_user foreign key (user_id) references users(id) on delete restrict
);

--5. Create table order_items [Dependent entity]
CREATE TABLE order_items (
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL check (quantity > 0),
    unit_price numeric(10, 2) NOT NULL check (unit_price >= 0),
    primary key (order_id, product_id),
    constraint fk_order_item_order foreign key (order_id) references orders(id) on delete cascade,
    constraint fk_order_item_product foreign key (product_id) references products(id) on delete restrict
);







