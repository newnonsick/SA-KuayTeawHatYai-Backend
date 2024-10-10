CREATE TABLE IF NOT EXISTS INGREDIENT (
    name VARCHAR(255) PRIMARY KEY,
    is_available BOOLEAN NOT NULL,
    image_URL VARCHAR(255),
    ingredient_type VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS MENU (
    name VARCHAR(255) PRIMARY KEY,
    category VARCHAR(255),
    price DECIMAL(10, 2) NOT NULL,
    image_URL VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS TABLES (
    table_number VARCHAR(10) PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS ORDERS (
    order_id SERIAL PRIMARY KEY,
    order_status VARCHAR(255),
    order_date DATE NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    table_number VARCHAR(10) REFERENCES TABLES(table_number)
);

CREATE TABLE IF NOT EXISTS ORDER_ITEM (
    order_item_id SERIAL PRIMARY KEY,
    menu_name VARCHAR(255) REFERENCES MENU(name),
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    portions VARCHAR(255),
    extra_info VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS ORDER_INGREDIENT (
    order_ingredient_id SERIAL PRIMARY KEY,
    order_item_id INT REFERENCES ORDER_ITEM(order_item_id),
    ingredient_name VARCHAR(255) REFERENCES INGREDIENT(name)
);

CREATE TABLE IF NOT EXISTS MENU_INGREDIENT (
    menu_name VARCHAR(255) REFERENCES MENU(name),
    ingredient_name VARCHAR(255) REFERENCES INGREDIENT(name),
    PRIMARY KEY (menu_name, ingredient_name)
);