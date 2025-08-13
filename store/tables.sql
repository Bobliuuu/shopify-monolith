-- Customers table
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    stripe_customer_id VARCHAR(255),
    total_spent DECIMAL(10,2) DEFAULT 0.00,
    order_count INTEGER DEFAULT 0,
    last_order_date TIMESTAMP,
    customer_io_id VARCHAR(255)
);

-- Products table (admin access)
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    compare_at_price DECIMAL(10,2),
    sku VARCHAR(100) UNIQUE,
    inventory_quantity INTEGER DEFAULT 0,
    weight DECIMAL(8,2),
    requires_shipping BOOLEAN DEFAULT true,
    taxable BOOLEAN DEFAULT true,
    status VARCHAR(20) DEFAULT 'active', -- active, draft, archived
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    vendor VARCHAR(100),
    product_type VARCHAR(100),
    tags TEXT[], -- PostgreSQL array for tags
    handle VARCHAR(255) UNIQUE, -- URL-friendly version of title
    seo_title VARCHAR(255),
    seo_description TEXT
);

-- Transactions table (admin access)
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, paid, failed, refunded, cancelled
    payment_status VARCHAR(20) DEFAULT 'pending', -- pending, paid, failed, refunded
    fulfillment_status VARCHAR(20) DEFAULT 'unfulfilled', -- unfulfilled, partial, fulfilled
    subtotal DECIMAL(10,2) NOT NULL,
    tax_amount DECIMAL(10,2) DEFAULT 0.00,
    shipping_amount DECIMAL(10,2) DEFAULT 0.00,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    total_amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    stripe_payment_intent_id VARCHAR(255),
    payment_method VARCHAR(50), -- card, crypto, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    customer_email VARCHAR(255),
    shipping_address JSONB,
    billing_address JSONB,
    line_items JSONB -- Store order items as JSON
);

-- Disputes table
CREATE TABLE disputes (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER REFERENCES transactions(id),
    stripe_dispute_id VARCHAR(255),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    reason VARCHAR(100),
    status VARCHAR(20), -- warning_needs_response, warning_under_review, warning_closed, needs_response, under_review, charge_refunded, won, lost
    evidence_details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_by TIMESTAMP,
    is_charge_refundable BOOLEAN DEFAULT false
);

-- Additional supporting tables
CREATE TABLE product_variants (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    title VARCHAR(255),
    price DECIMAL(10,2),
    sku VARCHAR(100),
    inventory_quantity INTEGER DEFAULT 0,
    weight DECIMAL(8,2),
    option1 VARCHAR(100), -- e.g., Size
    option2 VARCHAR(100), -- e.g., Color
    option3 VARCHAR(100), -- e.g., Material
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventory_logs (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    variant_id INTEGER REFERENCES product_variants(id),
    quantity_change INTEGER NOT NULL,
    reason VARCHAR(100), -- 'sale', 'restock', 'adjustment', 'return'
    reference_id INTEGER, -- transaction_id for sales
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);