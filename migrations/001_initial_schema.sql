CREATE TABLE IF NOT EXISTS INGREDIENT (
    name VARCHAR(100) PRIMARY KEY,
    is_available BOOLEAN NOT NULL,
    image_URL VARCHAR(255),
    ingredient_type VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS MENU (
    name VARCHAR(100) PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    image_URL VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS TABLES (
    table_number VARCHAR(5) PRIMARY KEY
);

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS ORDERS (
    order_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_status VARCHAR(20) NOT NULL DEFAULT 'รอทำอาหาร' CHECK(order_status IN ('รอทำอาหาร', 'กำลังทำอาหาร', 'รอเสิร์ฟ', 'เสร็จสิ้น')),
    order_datetime TIMESTAMP NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    table_number VARCHAR(5) REFERENCES TABLES(table_number) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS ORDER_ITEM (
    order_item_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    menu_name VARCHAR(100) REFERENCES MENU(name) ON DELETE CASCADE,
    order_id UUID REFERENCES ORDERS(order_id) ON DELETE CASCADE,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    portions VARCHAR(50),
    extra_info VARCHAR(255),
    orderitem_status VARCHAR(20) NOT NULL DEFAULT 'รอทำอาหาร' CHECK(orderitem_status IN ('รอทำอาหาร', 'กำลังทำอาหาร', 'เปลี่ยนวัตถุดิบ', 'เสร็จสิ้น'))
);

CREATE TABLE IF NOT EXISTS ORDER_INGREDIENT (
    order_ingredient_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_item_id UUID REFERENCES ORDER_ITEM(order_item_id) ON DELETE CASCADE,
    ingredient_name VARCHAR(100) REFERENCES INGREDIENT(name) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS MENU_INGREDIENT (
    menu_name VARCHAR(100) REFERENCES MENU(name) ON DELETE CASCADE,
    ingredient_name VARCHAR(100) REFERENCES INGREDIENT(name) ON DELETE CASCADE,
    PRIMARY KEY (menu_name, ingredient_name)
);
