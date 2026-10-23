CREATE DATABASE IF NOT EXISTS etl_demo;
USE etl_demo;

CREATE TABLE IF NOT EXISTS sales (
    order_id INT NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    order_date DATE NOT NULL,
    PRIMARY KEY (order_id)
);

INSERT INTO sales
    (order_id, customer_name, product_name, quantity, unit_price, order_date)
VALUES
    (1, 'Aarav', 'Keyboard', 2, 750.00, '2026-01-12'),
    (2, 'Diya', 'Mouse', 3, 400.00, '2026-01-18'),
    (3, 'Kabir', 'Keyboard', 1, 750.00, '2026-02-03'),
    (4, 'Meera', 'Monitor', 2, 8500.00, '2026-02-11'),
    (5, 'Ishaan', 'Mouse', 4, 400.00, '2026-02-20')
ON DUPLICATE KEY UPDATE
    customer_name = VALUES(customer_name),
    product_name = VALUES(product_name),
    quantity = VALUES(quantity),
    unit_price = VALUES(unit_price),
    order_date = VALUES(order_date);
