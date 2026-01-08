CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),-- for logs and tracking
    email VARCHAR(200) -- API handles validation 
);

--Assumed company owns warehouses
CREATE TABLE warehouses (
    id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(id),
    name VARCHAR(255) NOT NULL,
    address TEXT
);


CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(id),
    sku VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,       
    min_count INT DEFAULT 10, -- Determine low stocks
    UNIQUE (company_id, sku) -- each company have unique sku 
);


-- Solves that Products can be in multiple warehouses (many to many relationship)
CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id),
    warehouse_id INT REFERENCES warehouses(id),
    quantity INT NOT NULL DEFAULT 0 CHECK (quantity >= 0),-- check for logical correctness
    last_updated TIMESTAMP DEFAULT NOW(),
    UNIQUE (product_id, warehouse_id) -- added to prevent duplicate rows
);


-- Track when inventory levels change rather than overwriting 
CREATE TABLE inventory_logs (
    id SERIAL PRIMARY KEY,
    inventory_id INT REFERENCES inventory(id),
    change_amount INT NOT NULL, -- positive for add and negative for remove
    reason VARCHAR(50), -- like 'PURCHASE_ORDER', 'SALES_ORDER', 'DAMAGE'
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(id),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255)
);

-- Satisfies one product can be supplied by multiple vendors (many to many)
CREATE TABLE product_suppliers (
    product_id INT REFERENCES products(id),
    supplier_id INT REFERENCES suppliers(id),
    cost DECIMAL(10, 2),--each supplier might have different cost
    PRIMARY KEY (product_id, supplier_id)
);

-- To  handle Products containing other products
CREATE TABLE bundles (
    main_prod_id INT REFERENCES products(id), 
    inside_prod_id INT REFERENCES products(id), 
    quantity_req INT NOT NULL DEFAULT 1, -- how many products require to create bundle
    PRIMARY KEY (main_prod_id, inside_prod_id)
);
