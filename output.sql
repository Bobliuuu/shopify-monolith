-- Create products table if not exists
CREATE TABLE IF NOT EXISTS shopify_products (
  id BIGINT PRIMARY KEY,
  title VARCHAR(255),
  body_html TEXT,
  vendor VARCHAR(255),
  product_type VARCHAR(255),
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  published_at TIMESTAMP,
  handle VARCHAR(255),
  status VARCHAR(50),
  published_scope VARCHAR(50),
  tags TEXT,
  admin_graphql_api_id VARCHAR(255),
  total_inventory INTEGER DEFAULT 0,
  total_variants INTEGER DEFAULT 0,
  total_images INTEGER DEFAULT 0,
  total_options INTEGER DEFAULT 0
);

-- Insert products data
INSERT INTO shopify_products (
  id, title, body_html, vendor, product_type, created_at, updated_at, published_at,
  handle, status, published_scope, tags, admin_graphql_api_id,
  total_inventory, total_variants, total_images, total_options
) VALUES (
  9754834469111,
  'Gift Card',
  'This is a gift card for the store',
  'Snowboard Vendor',
  'giftcard',
  '2025-07-29T21:57:47-04:00',
  '2025-07-31T11:06:10-04:00',
  '2025-07-29T21:57:48-04:00',
  'gift-card',
  'active',
  'web',
  '',
  'gid://shopify/Product/9754834469111',
  0,
  4,
  1,
  1
);

INSERT INTO shopify_products (
  id, title, body_html, vendor, product_type, created_at, updated_at, published_at,
  handle, status, published_scope, tags, admin_graphql_api_id,
  total_inventory, total_variants, total_images, total_options
) VALUES (
  9754834567415,
  'Selling Plans Ski Wax',
  '',
  'Shop Monolith',
  'accessories',
  '2025-07-29T21:57:47-04:00',
  '2025-07-31T11:06:11-04:00',
  '2025-07-29T21:57:48-04:00',
  'selling-plans-ski-wax',
  'active',
  'web',
  'Accessory, Sport, Winter',
  'gid://shopify/Product/9754834567415',
  0,
  3,
  3,
  1
);

INSERT INTO shopify_products (
  id, title, body_html, vendor, product_type, created_at, updated_at, published_at,
  handle, status, published_scope, tags, admin_graphql_api_id,
  total_inventory, total_variants, total_images, total_options
) VALUES (
  9754834862327,
  'The 3p Fulfilled Snowboard',
  '',
  'Shop Monolith',
  'snowboard',
  '2025-07-29T21:57:48-04:00',
  '2025-07-31T11:06:12-04:00',
  '2025-07-29T21:57:48-04:00',
  'the-3p-fulfilled-snowboard',
  'active',
  'web',
  'Accessory, Sport, Winter',
  'gid://shopify/Product/9754834862327',
  0,
  1,
  1,
  1
);

INSERT INTO shopify_products (
  id, title, body_html, vendor, product_type, created_at, updated_at, published_at,
  handle, status, published_scope, tags, admin_graphql_api_id,
  total_inventory, total_variants, total_images, total_options
) VALUES (
  9754834796791,
  'The Archived Snowboard',
  '',
  'Snowboard Vendor',
  'snowboard',
  '2025-07-29T21:57:47-04:00',
  '2025-07-30T09:57:53-04:00',
  NULL,
  'the-archived-snowboard',
  'archived',
  'web',
  'Archived, Premium, Snow, Snowboard, Sport, Winter',
  'gid://shopify/Product/9754834796791',
  0,
  1,
  1,
  1
);

INSERT INTO shopify_products (
  id, title, body_html, vendor, product_type, created_at, updated_at, published_at,
  handle, status, published_scope, tags, admin_graphql_api_id,
  total_inventory, total_variants, total_images, total_options
) VALUES (
  9754834764023,
  'The Collection Snowboard: Hydrogen',
  '',
  'Hydrogen Vendor',
  'snowboard',
  '2025-07-29T21:57:47-04:00',
  '2025-07-31T11:30:47-04:00',
  '2025-07-29T21:57:49-04:00',
  'the-collection-snowboard-hydrogen',
  'active',
  'web',
  'Accessory, Sport, Winter',
  'gid://shopify/Product/9754834764023',
  0,
  1,
  1,
  1
);

INSERT INTO shopify_products (
  id, title, body_html, vendor, product_type, created_at, updated_at, published_at,
  handle, status, published_scope, tags, admin_graphql_api_id,
  total_inventory, total_variants, total_images, total_options
) VALUES (
  9754834960631,
  'The Collection Snowboard: Liquid',
  '',
  'Hydrogen Vendor',
  'snowboard',
  '2025-07-29T21:57:48-04:00',
  '2025-07-31T11:06:12-04:00',
  '2025-07-29T21:57:50-04:00',
  'the-collection-snowboard-liquid',
  'active',
  'web',
  'Accessory, Sport, Winter',
  'gid://shopify/Product/9754834960631',
  0,
  1,
  1,
  1
);

INSERT INTO shopify_products (
  id, title, body_html, vendor, product_type, created_at, updated_at, published_at,
  handle, status, published_scope, tags, admin_graphql_api_id,
  total_inventory, total_variants, total_images, total_options
) VALUES (
  9754834895095,
  'The Collection Snowboard: Oxygen',
  '',
  'Hydrogen Vendor',
  'snowboard',
  '2025-07-29T21:57:48-04:00',
  '2025-07-31T11:06:12-04:00',
  '2025-07-29T21:57:49-04:00',
  'the-collection-snowboard-oxygen',
  'active',
  'web',
  'Accessory, Sport, Winter',
  'gid://shopify/Product/9754834895095',
  0,
  1,
  1,
  1
);

INSERT INTO shopify_products (
  id, title, body_html, vendor, product_type, created_at, updated_at, published_at,
  handle, status, published_scope, tags, admin_graphql_api_id,
  total_inventory, total_variants, total_images, total_options
) VALUES (
  9754834534647,
  'The Compare at Price Snowboard',
  '',
  'Shop Monolith',
  'snowboard',
  '2025-07-29T21:57:47-04:00',
  '2025-07-31T11:06:10-04:00',
  '2025-07-29T21:57:48-04:00',
  'the-compare-at-price-snowboard',
  'active',
  'web',
  'Accessory, Sport, Winter',
  'gid://shopify/Product/9754834534647',
  0,
  1,
  1,
  1
);

INSERT INTO shopify_products (
  id, title, body_html, vendor, product_type, created_at, updated_at, published_at,
  handle, status, published_scope, tags, admin_graphql_api_id,
  total_inventory, total_variants, total_images, total_options
) VALUES (
  9754834665719,
  'The Complete Snowboard',
  'This <b>PREMIUM</b> <i>snowboard</i> is so <b>SUPER</b><i>DUPER</i> awesome!',
  'Snowboard Vendor',
  'snowboard',
  '2025-07-29T21:57:47-04:00',
  '2025-07-31T11:06:11-04:00',
  '2025-07-29T21:57:48-04:00',
  'the-complete-snowboard',
  'active',
  'web',
  'Premium, Snow, Snowboard, Sport, Winter',
  'gid://shopify/Product/9754834665719',
  0,
  5,
  1,
  1
);

INSERT INTO shopify_products (
  id, title, body_html, vendor, product_type, created_at, updated_at, published_at,
  handle, status, published_scope, tags, admin_graphql_api_id,
  total_inventory, total_variants, total_images, total_options
) VALUES (
  9754834600183,
  'The Draft Snowboard',
  '',
  'Snowboard Vendor',
  'snowboard',
  '2025-07-29T21:57:47-04:00',
  '2025-07-30T09:57:53-04:00',
  NULL,
  'the-draft-snowboard',
  'draft',
  'web',
  '',
  'gid://shopify/Product/9754834600183',
  0,
  1,
  1,
  1
);
