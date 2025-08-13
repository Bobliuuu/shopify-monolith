#!/usr/bin/env bun

/**
 * Database Reset Script
 * Drops all tables and recreates them with fresh schema
 * Usage: bun run db:reset
 */

import { Sequelize, DataTypes } from 'sequelize';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const DB_NAME = process.env.DB_NAME || 'snowboard_store';
const DB_USER = process.env.DB_USER || 'yb';
const DB_PASSWORD = process.env.DB_PASSWORD || '';
const DB_HOST = process.env.DB_HOST || 'localhost';
const DB_PORT = parseInt(process.env.DB_PORT || '5432');

async function resetDatabase(): Promise<void> {
  console.log('🗑️  Starting Database Reset...\n');
  
  // First connect to PostgreSQL without specifying a database
  const sequelizeAdmin = new Sequelize('postgres', DB_USER, DB_PASSWORD, {
    host: DB_HOST,
    port: DB_PORT,
    dialect: 'postgres',
    logging: false
  });

  try {
    // Test connection
    await sequelizeAdmin.authenticate();
    console.log('✅ Connected to PostgreSQL server');

    // Drop the database if it exists
    console.log(`🗑️  Dropping database "${DB_NAME}" if it exists...`);
    await sequelizeAdmin.query(`DROP DATABASE IF EXISTS "${DB_NAME}"`);
    console.log('✅ Database dropped successfully');

    // Create a fresh database
    console.log(`🆕 Creating fresh database "${DB_NAME}"...`);
    await sequelizeAdmin.query(`CREATE DATABASE "${DB_NAME}"`);
    console.log('✅ Fresh database created');

  } catch (error) {
    console.error('❌ Error during database reset:', error);
    throw error;
  } finally {
    await sequelizeAdmin.close();
  }

  // Now connect to the new database and create tables
  const sequelize = new Sequelize(DB_NAME, DB_USER, DB_PASSWORD, {
    host: DB_HOST,
    port: DB_PORT,
    dialect: 'postgres',
    logging: false
  });

  try {
    console.log('\n📋 Creating database schema...');

    // Create tables in the correct order (respecting foreign key dependencies)
    
    // 1. Customers table (no dependencies)
    await sequelize.query(`
      CREATE TABLE customers (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        first_name VARCHAR(255),
        last_name VARCHAR(255),
        phone VARCHAR(255),
        stripe_customer_id VARCHAR(255),
        total_spent DECIMAL(10,2) DEFAULT 0.00,
        order_count INTEGER DEFAULT 0,
        last_order_date TIMESTAMP,
        customer_io_id VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `);
    console.log('✅ Customers table created');

    // 2. Products table (no dependencies)
    await sequelize.query(`
      CREATE TABLE products (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        vendor VARCHAR(255),
        product_type VARCHAR(255),
        handle VARCHAR(255) UNIQUE,
        status VARCHAR(50) DEFAULT 'active',
        published_scope VARCHAR(50) DEFAULT 'web',
        tags TEXT,
        price DECIMAL(10,2),
        compare_at_price DECIMAL(10,2),
        cost_per_item DECIMAL(10,2),
        track_quantity BOOLEAN DEFAULT true,
        continue_selling_when_out_of_stock BOOLEAN DEFAULT false,
        inventory_quantity INTEGER DEFAULT 0,
        weight DECIMAL(8,2),
        weight_unit VARCHAR(10) DEFAULT 'kg',
        seo_title VARCHAR(255),
        seo_description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `);
    console.log('✅ Products table created');

    // 3. Product Variants table (depends on products)
    await sequelize.query(`
      CREATE TABLE product_variants (
        id SERIAL PRIMARY KEY,
        product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
        title VARCHAR(255),
        price DECIMAL(10,2),
        sku VARCHAR(255),
        inventory_quantity INTEGER DEFAULT 0,
        weight DECIMAL(8,2),
        option1 VARCHAR(255),
        option2 VARCHAR(255),
        option3 VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `);
    console.log('✅ Product Variants table created');

    // 4. Transactions table (depends on customers)
    await sequelize.query(`
      CREATE TABLE transactions (
        id SERIAL PRIMARY KEY,
        customer_id INTEGER REFERENCES customers(id) ON DELETE SET NULL,
        order_number VARCHAR(255) UNIQUE,
        status VARCHAR(50) DEFAULT 'pending',
        currency VARCHAR(3) DEFAULT 'USD',
        subtotal DECIMAL(10,2),
        tax_amount DECIMAL(10,2) DEFAULT 0.00,
        shipping_amount DECIMAL(10,2) DEFAULT 0.00,
        discount_amount DECIMAL(10,2) DEFAULT 0.00,
        total_amount DECIMAL(10,2) NOT NULL,
        payment_method VARCHAR(100),
        stripe_payment_intent_id VARCHAR(255),
        notes TEXT,
        customer_email VARCHAR(255),
        shipping_address JSONB,
        billing_address JSONB,
        line_items JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `);
    console.log('✅ Transactions table created');

    // 5. Disputes table (depends on transactions)
    await sequelize.query(`
      CREATE TABLE disputes (
        id SERIAL PRIMARY KEY,
        transaction_id INTEGER REFERENCES transactions(id) ON DELETE CASCADE,
        stripe_dispute_id VARCHAR(255),
        amount DECIMAL(10,2) NOT NULL,
        reason VARCHAR(255),
        status VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `);
    console.log('✅ Disputes table created');

    // 6. Inventory Logs table (depends on products and product_variants)
    await sequelize.query(`
      CREATE TABLE inventory_logs (
        id SERIAL PRIMARY KEY,
        product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
        variant_id INTEGER REFERENCES product_variants(id) ON DELETE CASCADE,
        quantity_change INTEGER NOT NULL,
        reason VARCHAR(255),
        reference_id INTEGER,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `);
    console.log('✅ Inventory Logs table created');

    // Create indexes for better performance
    console.log('\n🔍 Creating database indexes...');
    
    await sequelize.query('CREATE INDEX idx_customers_email ON customers(email);');
    await sequelize.query('CREATE INDEX idx_products_handle ON products(handle);');
    await sequelize.query('CREATE INDEX idx_transactions_customer_id ON transactions(customer_id);');
    await sequelize.query('CREATE INDEX idx_transactions_order_number ON transactions(order_number);');
    await sequelize.query('CREATE INDEX idx_disputes_transaction_id ON disputes(transaction_id);');
    
    console.log('✅ Database indexes created');

    console.log('\n🎉 Database reset completed successfully!');
    console.log('\n📝 Next steps:');
    console.log('1. Run "bun run seed" to populate with sample data');
    console.log('2. Run "bun run server" to start the application');
    console.log('3. Run "bun run test" to verify everything is working');

  } catch (error) {
    console.error('❌ Error creating schema:', error);
    throw error;
  } finally {
    await sequelize.close();
  }
}

// Run the reset
resetDatabase().catch(error => {
  console.error('💥 Database reset failed:', error);
  process.exit(1);
});
