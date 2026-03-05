-- Halal Seoul commerce_db schema v1
-- PostgreSQL 15+

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE users (
  user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT,
  name TEXT NOT NULL,
  auth_provider TEXT NOT NULL DEFAULT 'local',
  provider_user_id TEXT,
  role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE products (
  product_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  description TEXT,
  price_krw INTEGER NOT NULL CHECK (price_krw >= 0),
  sale_status TEXT NOT NULL DEFAULT '노출' CHECK (sale_status IN ('노출', '중지', '품절')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_products_sale_status ON products(sale_status);
CREATE INDEX idx_products_name ON products(name);

CREATE TABLE carts (
  cart_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE cart_items (
  cart_item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cart_id UUID NOT NULL REFERENCES carts(cart_id) ON DELETE CASCADE,
  product_id UUID NOT NULL REFERENCES products(product_id),
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  unit_price_krw INTEGER NOT NULL CHECK (unit_price_krw >= 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (cart_id, product_id)
);

CREATE TABLE orders (
  order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_number TEXT UNIQUE NOT NULL,
  user_id UUID NOT NULL REFERENCES users(user_id),
  status TEXT NOT NULL CHECK (status IN (
    'pending', 'paid', 'preparing', 'shipped', 'delivered',
    'cancel_requested', 'canceled'
  )),
  subtotal_krw INTEGER NOT NULL CHECK (subtotal_krw >= 0),
  shipping_fee_krw INTEGER NOT NULL DEFAULT 0 CHECK (shipping_fee_krw >= 0),
  discount_krw INTEGER NOT NULL DEFAULT 0 CHECK (discount_krw >= 0),
  total_krw INTEGER NOT NULL CHECK (total_krw >= 0),
  recipient_name TEXT NOT NULL,
  recipient_phone TEXT NOT NULL,
  shipping_line1 TEXT NOT NULL,
  shipping_line2 TEXT,
  shipping_postal_code TEXT NOT NULL,
  customs_clearance_number TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_orders_user_created ON orders(user_id, created_at DESC);
CREATE INDEX idx_orders_status ON orders(status);

CREATE TABLE order_items (
  order_item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id UUID NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
  product_id UUID NOT NULL REFERENCES products(product_id),
  unit_price_krw INTEGER NOT NULL CHECK (unit_price_krw >= 0),
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE payments (
  payment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id UUID NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
  provider TEXT NOT NULL DEFAULT 'toss_payments',
  payment_key TEXT UNIQUE,
  amount_krw INTEGER NOT NULL CHECK (amount_krw >= 0),
  status TEXT NOT NULL CHECK (status IN ('ready', 'confirmed', 'failed', 'canceled')),
  approved_at TIMESTAMPTZ,
  failure_code TEXT,
  failure_message TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_payments_order ON payments(order_id);
CREATE INDEX idx_payments_status ON payments(status);

CREATE TABLE refunds (
  refund_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id UUID NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
  payment_id UUID NOT NULL REFERENCES payments(payment_id) ON DELETE CASCADE,
  refund_type TEXT NOT NULL CHECK (refund_type IN ('full', 'partial')),
  amount_krw INTEGER NOT NULL CHECK (amount_krw >= 0),
  status TEXT NOT NULL CHECK (status IN ('requested', 'approved', 'rejected', 'completed')),
  reason TEXT,
  provider_refund_id TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE refund_items (
  refund_item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  refund_id UUID NOT NULL REFERENCES refunds(refund_id) ON DELETE CASCADE,
  order_item_id UUID NOT NULL REFERENCES order_items(order_item_id),
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  amount_krw INTEGER NOT NULL CHECK (amount_krw >= 0)
);
