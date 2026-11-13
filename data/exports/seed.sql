-- Synthetic Seed Data for Abandoned Cart Recovery System
-- Scale: Synthetic Data Generator (Seed: 20261022)

INSERT INTO products (product_id, sku, name, category, price, is_active) VALUES ('PRD-000001', 'SKU-ELE-0001', 'Ultra-Light Ergonomic Keyboard', 'Electronics', 129.99, 1) ON DUPLICATE KEY UPDATE is_active=1;
INSERT INTO products (product_id, sku, name, category, price, is_active) VALUES ('PRD-000002', 'SKU-ELE-0002', 'Wireless Noise-Cancelling Headphones', 'Electronics', 249.95, 1) ON DUPLICATE KEY UPDATE is_active=1;
INSERT INTO products (product_id, sku, name, category, price, is_active) VALUES ('PRD-000003', 'SKU-ELE-0003', 'Precision Optical Gaming Mouse', 'Electronics', 69.5, 1) ON DUPLICATE KEY UPDATE is_active=1;
INSERT INTO products (product_id, sku, name, category, price, is_active) VALUES ('PRD-000004', 'SKU-ELE-0004', '4K Ultra-HD 27-inch Monitor', 'Electronics', 389.0, 1) ON DUPLICATE KEY UPDATE is_active=1;
INSERT INTO products (product_id, sku, name, category, price, is_active) VALUES ('PRD-000005', 'SKU-ACC-0005', 'USB-C Multi-Port Hub Pro', 'Accessories', 49.99, 1) ON DUPLICATE KEY UPDATE is_active=1;
INSERT INTO products (product_id, sku, name, category, price, is_active) VALUES ('PRD-000006', 'SKU-FIT-0006', 'Hydro-Shield Stainless Water Bottle', 'Fitness', 34.5, 1) ON DUPLICATE KEY UPDATE is_active=1;
INSERT INTO products (product_id, sku, name, category, price, is_active) VALUES ('PRD-000007', 'SKU-APP-0007', 'Organic Cotton Minimalist Hoodie', 'Apparel', 78.0, 1) ON DUPLICATE KEY UPDATE is_active=1;
INSERT INTO products (product_id, sku, name, category, price, is_active) VALUES ('PRD-000008', 'SKU-APP-0008', 'Full-Grain Leather Work Backpack', 'Apparel', 185.0, 1) ON DUPLICATE KEY UPDATE is_active=1;
INSERT INTO products (product_id, sku, name, category, price, is_active) VALUES ('PRD-000009', 'SKU-FIT-0009', 'Smart Fitness & Sleep Tracker Band', 'Fitness', 99.95, 1) ON DUPLICATE KEY UPDATE is_active=1;
INSERT INTO products (product_id, sku, name, category, price, is_active) VALUES ('PRD-000010', 'SKU-HOM-0010', 'Aroma Cold-Brew Coffee Maker', 'Home', 54.0, 1) ON DUPLICATE KEY UPDATE is_active=1;
INSERT INTO products (product_id, sku, name, category, price, is_active) VALUES ('PRD-000011', 'SKU-HOM-0011', 'Ceramic Matte Dinnerware Set 16pc', 'Home', 115.0, 1) ON DUPLICATE KEY UPDATE is_active=1;
INSERT INTO products (product_id, sku, name, category, price, is_active) VALUES ('PRD-000012', 'SKU-OUT-0012', 'Titanium Lightweight Camping Stove', 'Outdoor', 45.99, 1) ON DUPLICATE KEY UPDATE is_active=1;
INSERT INTO products (product_id, sku, name, category, price, is_active) VALUES ('PRD-000013', 'SKU-APP-0013', 'Merino Wool Breathable Socks (3pk)', 'Apparel', 28.5, 1) ON DUPLICATE KEY UPDATE is_active=1;
INSERT INTO products (product_id, sku, name, category, price, is_active) VALUES ('PRD-000014', 'SKU-HOM-0014', 'Smart Ambient RGB Desk Lamp', 'Home', 62.0, 1) ON DUPLICATE KEY UPDATE is_active=1;
INSERT INTO products (product_id, sku, name, category, price, is_active) VALUES ('PRD-000015', 'SKU-STA-0015', 'Mechanical Pencil Drafting Set', 'Stationery', 24.99, 1) ON DUPLICATE KEY UPDATE is_active=1;
INSERT INTO products (product_id, sku, name, category, price, is_active) VALUES ('PRD-000016', 'SKU-ACC-0016', 'Polarized UV-Protection Sunglasses', 'Accessories', 89.0, 1) ON DUPLICATE KEY UPDATE is_active=1;
INSERT INTO products (product_id, sku, name, category, price, is_active) VALUES ('PRD-000017', 'SKU-ELE-0017', 'Compact Magnetic Power Bank 10000mAh', 'Electronics', 42.0, 1) ON DUPLICATE KEY UPDATE is_active=1;
INSERT INTO products (product_id, sku, name, category, price, is_active) VALUES ('PRD-000018', 'SKU-FIT-0018', 'Eco-Friendly Yoga Mat with Alignment', 'Fitness', 58.0, 1) ON DUPLICATE KEY UPDATE is_active=1;
INSERT INTO products (product_id, sku, name, category, price, is_active) VALUES ('PRD-000019', 'SKU-OUT-0019', 'Aerodynamic Cycling Helmet', 'Outdoor', 110.0, 1) ON DUPLICATE KEY UPDATE is_active=1;
INSERT INTO products (product_id, sku, name, category, price, is_active) VALUES ('PRD-000020', 'SKU-ELE-0020', 'Acoustic Walnut Desktop Speakers', 'Electronics', 195.0, 1) ON DUPLICATE KEY UPDATE is_active=1;
INSERT INTO campaigns (campaign_id, name, channel, trigger_delay_minutes, discount_percent, is_active, created_at) VALUES ('CMP-2026-000001', 'Standard Cart Recovery Email (10% Off)', 'EMAIL', 60, 10.0, 1, '2026-10-01 08:00:00');
INSERT INTO campaigns (campaign_id, name, channel, trigger_delay_minutes, discount_percent, is_active, created_at) VALUES ('CMP-2026-000002', 'Express SMS Flash Recovery (15% Off)', 'SMS', 60, 15.0, 1, '2026-10-01 08:00:00');
INSERT INTO campaigns (campaign_id, name, channel, trigger_delay_minutes, discount_percent, is_active, created_at) VALUES ('CMP-2026-000003', 'VIP Cart Re-engagement Email (15% Off)', 'EMAIL', 120, 15.0, 1, '2026-10-01 08:00:00');
