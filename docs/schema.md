# Relational Database Schema Specification
## MySQL 8 & SQLite Dual-Engine Architecture

### 1. Database Schema DDL (SQLAlchemy 2.0 / Alembic)

```sql
-- Customers Master Table
CREATE TABLE customers (
    customer_id VARCHAR(32) NOT NULL PRIMARY KEY,
    first_name VARCHAR(64) NOT NULL,
    last_name VARCHAR(64) NOT NULL,
    email VARCHAR(128) NOT NULL,
    phone VARCHAR(32) NOT NULL,
    preferred_channel VARCHAR(16) NOT NULL DEFAULT 'EMAIL',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
CREATE INDEX ix_customers_email ON customers(email);
CREATE INDEX ix_customers_phone ON customers(phone);
CREATE INDEX ix_customers_created_at ON customers(created_at);

-- Products Catalog Master Table
CREATE TABLE products (
    product_id VARCHAR(32) NOT NULL PRIMARY KEY,
    sku VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(128) NOT NULL,
    category VARCHAR(64) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1
);
CREATE INDEX ix_products_category ON products(category);

-- Consents Audit Table
CREATE TABLE consents (
    consent_id VARCHAR(32) NOT NULL PRIMARY KEY,
    customer_id VARCHAR(32) NOT NULL,
    channel VARCHAR(16) NOT NULL,
    status VARCHAR(16) NOT NULL,
    effective_at DATETIME NOT NULL,
    source VARCHAR(64) NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);
CREATE INDEX ix_consents_customer_channel_effective ON consents(customer_id, channel, effective_at);

-- Sessions Table
CREATE TABLE sessions (
    session_id VARCHAR(32) NOT NULL PRIMARY KEY,
    customer_id VARCHAR(32) NOT NULL,
    device_type VARCHAR(32) NOT NULL DEFAULT 'DESKTOP',
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    started_at DATETIME NOT NULL,
    ended_at DATETIME,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);
CREATE INDEX ix_sessions_customer_id ON sessions(customer_id);
CREATE INDEX ix_sessions_started_at ON sessions(started_at);

-- Carts Table
CREATE TABLE carts (
    cart_id VARCHAR(32) NOT NULL PRIMARY KEY,
    customer_id VARCHAR(32) NOT NULL,
    session_id VARCHAR(32),
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    subtotal DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    discount_total DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    last_activity_at DATETIME NOT NULL,
    abandoned_at DATETIME,
    recovered_at DATETIME,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE SET NULL
);
CREATE INDEX ix_carts_customer_status ON carts(customer_id, status);
CREATE INDEX ix_carts_status_last_activity ON carts(status, last_activity_at);
CREATE INDEX ix_carts_abandoned_at ON carts(abandoned_at);

-- Cart Lines Table
CREATE TABLE cart_lines (
    cart_line_id VARCHAR(48) NOT NULL PRIMARY KEY,
    cart_id VARCHAR(32) NOT NULL,
    product_id VARCHAR(32) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (cart_id) REFERENCES carts(cart_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
);
CREATE INDEX ix_cart_lines_cart_product ON cart_lines(cart_id, product_id);

-- Campaigns Master Table
CREATE TABLE campaigns (
    campaign_id VARCHAR(32) NOT NULL PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    channel VARCHAR(16) NOT NULL,
    trigger_delay_minutes INTEGER NOT NULL DEFAULT 60,
    discount_percent DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL
);

-- Message Templates Table
CREATE TABLE message_templates (
    template_id VARCHAR(32) NOT NULL PRIMARY KEY,
    campaign_id VARCHAR(32) NOT NULL,
    channel VARCHAR(16) NOT NULL,
    variant VARCHAR(8) NOT NULL DEFAULT 'A',
    subject VARCHAR(255),
    body_template VARCHAR(1024) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id) ON DELETE CASCADE
);
CREATE INDEX ix_message_templates_campaign_id ON message_templates(campaign_id);

-- Send Attempts Log Table
CREATE TABLE send_attempts (
    send_id VARCHAR(32) NOT NULL PRIMARY KEY,
    message_id VARCHAR(64) NOT NULL,
    campaign_id VARCHAR(32) NOT NULL,
    template_id VARCHAR(32),
    cart_id VARCHAR(32) NOT NULL,
    customer_id VARCHAR(32) NOT NULL,
    channel VARCHAR(16) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'QUEUED',
    suppression_reason VARCHAR(64),
    scheduled_at DATETIME NOT NULL,
    sent_at DATETIME,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES message_templates(template_id) ON DELETE SET NULL,
    FOREIGN KEY (cart_id) REFERENCES carts(cart_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);
CREATE INDEX ix_send_attempts_customer_channel_sent ON send_attempts(customer_id, channel, sent_at);
CREATE INDEX ix_send_attempts_cart_campaign ON send_attempts(cart_id, campaign_id);

-- Communication Events Telemetry Table
CREATE TABLE communication_events (
    event_id VARCHAR(32) NOT NULL PRIMARY KEY,
    send_id VARCHAR(32) NOT NULL,
    event_type VARCHAR(32) NOT NULL,
    timestamp DATETIME NOT NULL,
    metadata_json TEXT,
    FOREIGN KEY (send_id) REFERENCES send_attempts(send_id) ON DELETE CASCADE
);
CREATE INDEX ix_comm_events_send_type_time ON communication_events(send_id, event_type, timestamp);

-- Orders Table
CREATE TABLE orders (
    order_id VARCHAR(32) NOT NULL PRIMARY KEY,
    customer_id VARCHAR(32) NOT NULL,
    cart_id VARCHAR(32),
    total_amount DECIMAL(10, 2) NOT NULL,
    order_timestamp DATETIME NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'COMPLETED',
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (cart_id) REFERENCES carts(cart_id) ON DELETE SET NULL
);
CREATE INDEX ix_orders_customer_timestamp ON orders(customer_id, order_timestamp);

-- Order Lines Table
CREATE TABLE order_lines (
    order_line_id VARCHAR(48) NOT NULL PRIMARY KEY,
    order_id VARCHAR(32) NOT NULL,
    product_id VARCHAR(32) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
);
CREATE INDEX ix_order_lines_order_id ON order_lines(order_id);

-- Attributions Table
CREATE TABLE attributions (
    attribution_id VARCHAR(32) NOT NULL PRIMARY KEY,
    order_id VARCHAR(32) NOT NULL UNIQUE,
    send_id VARCHAR(32) NOT NULL,
    campaign_id VARCHAR(32) NOT NULL,
    cart_id VARCHAR(32),
    order_timestamp DATETIME NOT NULL,
    qualifying_click_at DATETIME NOT NULL,
    latency_hours INTEGER NOT NULL DEFAULT 0,
    attributed_revenue DECIMAL(10, 2) NOT NULL,
    model VARCHAR(32) NOT NULL DEFAULT 'LAST_CLICK',
    created_at DATETIME NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (send_id) REFERENCES send_attempts(send_id) ON DELETE CASCADE,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    FOREIGN KEY (cart_id) REFERENCES carts(cart_id) ON DELETE SET NULL
);
CREATE INDEX ix_attributions_campaign_order_time ON attributions(campaign_id, order_timestamp);

-- Anomaly Records Table
CREATE TABLE anomaly_records (
    anomaly_id VARCHAR(32) NOT NULL PRIMARY KEY,
    issue_type VARCHAR(64) NOT NULL,
    affected_entity VARCHAR(64) NOT NULL,
    affected_record_id VARCHAR(64) NOT NULL,
    detected_at DATETIME NOT NULL,
    observed_value TEXT NOT NULL,
    expected_value TEXT NOT NULL,
    ground_truth_label VARCHAR(64) NOT NULL,
    expected_decision VARCHAR(128) NOT NULL,
    actual_decision VARCHAR(128) NOT NULL,
    resolution_status VARCHAR(32) NOT NULL DEFAULT 'DETECTED'
);
CREATE INDEX ix_anomalies_issue_entity ON anomaly_records(issue_type, affected_entity);
```

