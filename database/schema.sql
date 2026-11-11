-- database/schema.sql

-- ------------------------------------------------------------
-- Database: campuseats
-- ------------------------------------------------------------

-- 1. Users table (students, staff, admin)
CREATE TABLE users (
    id          SERIAL PRIMARY KEY,
    email       VARCHAR(255) UNIQUE NOT NULL,
    password    VARCHAR(255) NOT NULL,               -- bcrypt hash
    full_name   VARCHAR(255) NOT NULL,
    role        VARCHAR(20) NOT NULL CHECK (role IN ('student', 'staff', 'admin')),
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 2. Categories for food items (e.g., "Beverages", "Snacks")
CREATE TABLE categories (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

-- 3. Food items
CREATE TABLE food_items (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(150) NOT NULL,
    description TEXT,
    price       NUMERIC(8,2) NOT NULL CHECK (price >= 0),
    category_id INT REFERENCES categories(id) ON DELETE SET NULL,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 4. Ingredients (inventory master list)
CREATE TABLE ingredients (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(150) UNIQUE NOT NULL,
    quantity    INT NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    unit        VARCHAR(50) NOT NULL,                -- e.g., "g", "pcs"
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 5. Recipes – many‑to‑many relationship between food_items and ingredients
CREATE TABLE recipes (
    food_item_id INT REFERENCES food_items(id) ON DELETE CASCADE,
    ingredient_id INT REFERENCES ingredients(id) ON DELETE CASCADE,
    amount       NUMERIC(8,2) NOT NULL CHECK (amount > 0),
    unit         VARCHAR(50) NOT NULL,
    PRIMARY KEY (food_item_id, ingredient_id)
);

-- 6. Orders (student orders)
CREATE TABLE orders (
    id          SERIAL PRIMARY KEY,
    user_id     INT REFERENCES users(id) ON DELETE CASCADE,
    status      VARCHAR(20) NOT NULL CHECK (status IN ('pending','accepted','preparing','ready','completed','rejected')),
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at  TIMESTAMP WITH TIME ZONE
);

-- 7. Order items (line items for an order)
CREATE TABLE order_items (
    id            SERIAL PRIMARY KEY,
    order_id      INT REFERENCES orders(id) ON DELETE CASCADE,
    food_item_id  INT REFERENCES food_items(id) ON DELETE RESTRICT,
    quantity      INT NOT NULL CHECK (quantity > 0),
    unit_price    NUMERIC(8,2) NOT NULL CHECK (unit_price >= 0)
);

-- 8. Payments (one‑to‑one with an order for this demo)
CREATE TABLE payments (
    id          SERIAL PRIMARY KEY,
    order_id    INT UNIQUE REFERENCES orders(id) ON DELETE CASCADE,
    method      VARCHAR(30) NOT NULL CHECK (method IN ('cash','demo')),  -- demo payment method for the project
    amount      NUMERIC(10,2) NOT NULL CHECK (amount >= 0),
    paid_at     TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 9. Inventory transactions (audit trail for stock changes)
CREATE TABLE inventory_transactions (
    id          SERIAL PRIMARY KEY,
    ingredient_id INT REFERENCES ingredients(id) ON DELETE CASCADE,
    delta       INT NOT NULL,                -- positive = addition, negative = deduction
    note        TEXT,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- ------------------------------------------------------------
-- Indexes for faster look‑ups
-- ------------------------------------------------------------
CREATE INDEX idx_food_category ON food_items(category_id);
CREATE INDEX idx_order_user ON orders(user_id);
CREATE INDEX idx_order_status ON orders(status);
CREATE INDEX idx_order_item_order ON order_items(order_id);
CREATE INDEX idx_inventory_ingredient ON inventory_transactions(ingredient_id);

-- ------------------------------------------------------------
-- Sample data (demo accounts, categories, foods, ingredients, recipes)
-- ------------------------------------------------------------

-- Demo users (passwords are bcrypt hashes for: adminpass, staffpass, studentpass)
INSERT INTO users (email, password, full_name, role) VALUES
('admin@campuseats.edu',   '$2b$12$KIXF0a2N6QDvnocYhqK0OO8i/5jB38p9K/9ZR5UaKdE68HwRzbHby', 'Admin User',   'admin'),
('staff@campuseats.edu',   '$2b$12$u1Z9Y6YmK5sGQ5yI9QzSPOv7i3/FY9VZjX1c6W0LHSO6ZQ/5ZK9iW', 'Staff Member', 'staff'),
('student@campuseats.edu', '$2b$12$Dc1UjM/KBW0LzNKBT6e0lOUH4dWcPSNQOU3UvW5vKWDNlVHlWJMYK', 'Student User', 'student');

-- Categories
INSERT INTO categories (name, description) VALUES
('Beverages', 'Cold & hot drinks'),
('Snacks',    'Quick bites'),
('Main Course','Full meals');

-- Ingredients (stock will be adjusted by staff)
INSERT INTO ingredients (name, quantity, unit) VALUES
('Coffee Beans', 5000, 'g'),
('Milk',         200, 'l'),
('Bread',        100, 'pcs'),
('Cheese',        50, 'pcs'),
('Tomato',       200, 'pcs');

-- Food items
INSERT INTO food_items (name, description, price, category_id) VALUES
('Cappuccino', 'Espresso with steamed milk', 3.50, (SELECT id FROM categories WHERE name = 'Beverages')),
('Cheese Sandwich', 'Grilled sandwich with cheese', 2.75, (SELECT id FROM categories WHERE name = 'Snacks')),
('Veggie Wrap', 'Wrap with fresh veggies', 4.20, (SELECT id FROM categories WHERE name = 'Main Course'));

-- Recipes – linking foods to ingredients
INSERT INTO recipes (food_item_id, ingredient_id, amount, unit) VALUES
-- Cappuccino
((SELECT id FROM food_items WHERE name='Cappuccino'), (SELECT id FROM ingredients WHERE name='Coffee Beans'), 15, 'g'),
((SELECT id FROM food_items WHERE name='Cappuccino'), (SELECT id FROM ingredients WHERE name='Milk'), 0.2, 'l'),
-- Cheese Sandwich
((SELECT id FROM food_items WHERE name='Cheese Sandwich'), (SELECT id FROM ingredients WHERE name='Bread'), 2, 'pcs'),
((SELECT id FROM food_items WHERE name='Cheese Sandwich'), (SELECT id FROM ingredients WHERE name='Cheese'), 1, 'pcs'),
-- Veggie Wrap
((SELECT id FROM food_items WHERE name='Veggie Wrap'), (SELECT id FROM ingredients WHERE name='Bread'), 1, 'pcs'),
((SELECT id FROM food_items WHERE name='Veggie Wrap'), (SELECT id FROM ingredients WHERE name='Tomato'), 2, 'pcs');

-- Note: No orders are pre‑populated; they will be created via the API.
