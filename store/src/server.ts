import express, { Request, Response } from 'express';
import { Sequelize, DataTypes, Model, Optional } from 'sequelize';
import Stripe from 'stripe';
import cors from 'cors';
import path from 'path';
import dotenv from 'dotenv';
import { ServiceManager } from './services/index';

dotenv.config();

const app = express();

// Middleware
app.use(express.json());
app.use(cors());
app.use(express.static('dist'));
// Initialize Stripe
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || '', {
  apiVersion: '2025-07-30.basil',
});

// Initialize service manager for GA4 and Customer.io
const serviceManager = ServiceManager.getInstance();
try {
  serviceManager.initFromEnvironment();
  console.log('Analytics services initialized successfully');
} catch (error) {
  console.warn('Analytics services not fully configured:', (error as Error).message);
}

// Database connection
const sequelize = new Sequelize(
  process.env.DB_NAME || 'snowboard_store',
  process.env.DB_USER || 'postgres',
  process.env.DB_PASS || 'password',
  {
    host: process.env.DB_HOST || 'localhost',
    dialect: 'postgres',
    logging: false
  }
);

// Interface definitions
interface CustomerAttributes {
  id: number;
  email: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  stripe_customer_id?: string;
  total_spent: number;
  order_count: number;
  last_order_date?: Date;
  customer_io_id?: string;
  created_at?: Date;
  updated_at?: Date;
}

interface CustomerCreationAttributes extends Optional<CustomerAttributes, 'id' | 'total_spent' | 'order_count' | 'created_at' | 'updated_at'> {}

interface ProductAttributes {
  id: number;
  title: string;
  description?: string;
  price: number;
  compare_at_price?: number;
  sku?: string;
  inventory_quantity: number;
  weight?: number;
  requires_shipping: boolean;
  taxable: boolean;
  status: string;
  vendor?: string;
  product_type?: string;
  tags?: string[];
  handle?: string;
  seo_title?: string;
  seo_description?: string;
  created_at?: Date;
  updated_at?: Date;
}

interface ProductCreationAttributes extends Optional<ProductAttributes, 'id' | 'inventory_quantity' | 'requires_shipping' | 'taxable' | 'status' | 'created_at' | 'updated_at'> {}

interface TransactionAttributes {
  id: number;
  customer_id?: number;
  order_number: string;
  status: string;
  payment_status: string;
  fulfillment_status: string;
  subtotal: number;
  tax_amount: number;
  shipping_amount: number;
  discount_amount: number;
  total_amount: number;
  payment_method?: string;
  stripe_payment_intent_id?: string;
  notes?: string;
  customer_email?: string;
  shipping_address?: object;
  billing_address?: object;
  line_items?: object;
  created_at?: Date;
  updated_at?: Date;
}

interface TransactionCreationAttributes extends Optional<TransactionAttributes, 'id' | 'status' | 'payment_status' | 'fulfillment_status' | 'tax_amount' | 'shipping_amount' | 'discount_amount' | 'created_at' | 'updated_at'> {}

interface DisputeAttributes {
  id: number;
  transaction_id?: number;
  stripe_dispute_id?: string;
  amount: number;
  reason?: string;
  status?: string;
  created_at?: Date;
}

interface DisputeCreationAttributes extends Optional<DisputeAttributes, 'id' | 'created_at'> {}

interface ProductVariantAttributes {
  id: number;
  product_id?: number;
  title?: string;
  price?: number;
  sku?: string;
  inventory_quantity: number;
  weight?: number;
  option1?: string;
  option2?: string;
  option3?: string;
  created_at?: Date;
}

interface ProductVariantCreationAttributes extends Optional<ProductVariantAttributes, 'id' | 'inventory_quantity' | 'created_at'> {}

interface InventoryLogAttributes {
  id: number;
  product_id?: number;
  variant_id?: number;
  quantity_change: number;
  reason?: string;
  reference_id?: number;
  notes?: string;
  created_at?: Date;
}

interface InventoryLogCreationAttributes extends Optional<InventoryLogAttributes, 'id' | 'created_at'> {}

// Model classes
class Customer extends Model<CustomerAttributes, CustomerCreationAttributes> implements CustomerAttributes {
  declare id: number;
  declare email: string;
  declare first_name?: string;
  declare last_name?: string;
  declare phone?: string;
  declare stripe_customer_id?: string;
  declare total_spent: number;
  declare order_count: number;
  declare last_order_date?: Date;
  declare customer_io_id?: string;
  declare readonly created_at: Date;
  declare readonly updated_at: Date;
}

class Product extends Model<ProductAttributes, ProductCreationAttributes> implements ProductAttributes {
  declare id: number;
  declare title: string;
  declare description?: string;
  declare price: number;
  declare compare_at_price?: number;
  declare sku?: string;
  declare inventory_quantity: number;
  declare weight?: number;
  declare requires_shipping: boolean;
  declare taxable: boolean;
  declare status: string;
  declare vendor?: string;
  declare product_type?: string;
  declare tags?: string[];
  declare handle?: string;
  declare seo_title?: string;
  declare seo_description?: string;
  declare readonly created_at: Date;
  declare readonly updated_at: Date;
}

class Transaction extends Model<TransactionAttributes, TransactionCreationAttributes> implements TransactionAttributes {
  declare id: number;
  declare customer_id?: number;
  declare order_number: string;
  declare status: string;
  declare payment_status: string;
  declare fulfillment_status: string;
  declare subtotal: number;
  declare tax_amount: number;
  declare shipping_amount: number;
  declare discount_amount: number;
  declare total_amount: number;
  declare payment_method?: string;
  declare stripe_payment_intent_id?: string;
  declare notes?: string;
  declare customer_email?: string;
  declare shipping_address?: object;
  declare billing_address?: object;
  declare line_items?: object;
  declare readonly created_at: Date;
  declare readonly updated_at: Date;
}

class Dispute extends Model<DisputeAttributes, DisputeCreationAttributes> implements DisputeAttributes {
  declare id: number;
  declare transaction_id?: number;
  declare stripe_dispute_id?: string;
  declare amount: number;
  declare reason?: string;
  declare status?: string;
  declare readonly created_at: Date;
}

class ProductVariant extends Model<ProductVariantAttributes, ProductVariantCreationAttributes> implements ProductVariantAttributes {
  declare id: number;
  declare product_id?: number;
  declare title?: string;
  declare price?: number;
  declare sku?: string;
  declare inventory_quantity: number;
  declare weight?: number;
  declare option1?: string;
  declare option2?: string;
  declare option3?: string;
  declare readonly created_at: Date;
}

class InventoryLog extends Model<InventoryLogAttributes, InventoryLogCreationAttributes> implements InventoryLogAttributes {
  declare id: number;
  declare product_id?: number;
  declare variant_id?: number;
  declare quantity_change: number;
  declare reason?: string;
  declare reference_id?: number;
  declare notes?: string;
  declare readonly created_at: Date;
}

// Initialize models
Customer.init({
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  email: {
    type: DataTypes.STRING,
    unique: true,
    allowNull: false
  },
  first_name: DataTypes.STRING,
  last_name: DataTypes.STRING,
  phone: DataTypes.STRING,
  stripe_customer_id: DataTypes.STRING,
  total_spent: {
    type: DataTypes.DECIMAL(10, 2),
    defaultValue: 0.00
  },
  order_count: {
    type: DataTypes.INTEGER,
    defaultValue: 0
  },
  last_order_date: DataTypes.DATE,
  customer_io_id: DataTypes.STRING
}, {
  sequelize,
  tableName: 'customers',
  timestamps: true,
  createdAt: 'created_at',
  updatedAt: 'updated_at'
});

Product.init({
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  title: {
    type: DataTypes.STRING,
    allowNull: false
  },
  description: DataTypes.TEXT,
  price: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: false
  },
  compare_at_price: DataTypes.DECIMAL(10, 2),
  sku: {
    type: DataTypes.STRING,
    unique: true
  },
  inventory_quantity: {
    type: DataTypes.INTEGER,
    defaultValue: 0
  },
  weight: DataTypes.DECIMAL(8, 2),
  requires_shipping: {
    type: DataTypes.BOOLEAN,
    defaultValue: true
  },
  taxable: {
    type: DataTypes.BOOLEAN,
    defaultValue: true
  },
  status: {
    type: DataTypes.STRING,
    defaultValue: 'active'
  },
  vendor: DataTypes.STRING,
  product_type: DataTypes.STRING,
  tags: DataTypes.ARRAY(DataTypes.STRING),
  handle: {
    type: DataTypes.STRING,
    unique: true
  },
  seo_title: DataTypes.STRING,
  seo_description: DataTypes.TEXT
}, {
  sequelize,
  tableName: 'products',
  timestamps: true,
  createdAt: 'created_at',
  updatedAt: 'updated_at'
});

Transaction.init({
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  customer_id: {
    type: DataTypes.INTEGER,
    references: {
      model: Customer,
      key: 'id'
    }
  },
  order_number: {
    type: DataTypes.STRING,
    unique: true,
    allowNull: false
  },
  status: {
    type: DataTypes.STRING,
    defaultValue: 'pending'
  },
  payment_status: {
    type: DataTypes.STRING,
    defaultValue: 'pending'
  },
  fulfillment_status: {
    type: DataTypes.STRING,
    defaultValue: 'unfulfilled'
  },
  subtotal: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: false
  },
  tax_amount: {
    type: DataTypes.DECIMAL(10, 2),
    defaultValue: 0.00
  },
  shipping_amount: {
    type: DataTypes.DECIMAL(10, 2),
    defaultValue: 0.00
  },
  discount_amount: {
    type: DataTypes.DECIMAL(10, 2),
    defaultValue: 0.00
  },
  total_amount: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: false
  },
  payment_method: DataTypes.STRING,
  stripe_payment_intent_id: DataTypes.STRING,
  notes: DataTypes.TEXT,
  customer_email: DataTypes.STRING,
  shipping_address: DataTypes.JSONB,
  billing_address: DataTypes.JSONB,
  line_items: DataTypes.JSONB
}, {
  sequelize,
  tableName: 'transactions',
  timestamps: true,
  createdAt: 'created_at',
  updatedAt: 'updated_at'
});

Dispute.init({
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  transaction_id: {
    type: DataTypes.INTEGER,
    references: {
      model: Transaction,
      key: 'id'
    }
  },
  stripe_dispute_id: DataTypes.STRING,
  amount: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: false
  },
  reason: DataTypes.STRING,
  status: DataTypes.STRING
}, {
  sequelize,
  tableName: 'disputes',
  timestamps: true,
  createdAt: 'created_at',
  updatedAt: false
});

ProductVariant.init({
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  product_id: {
    type: DataTypes.INTEGER,
    references: {
      model: Product,
      key: 'id'
    }
  },
  title: DataTypes.STRING,
  price: DataTypes.DECIMAL(10, 2),
  sku: DataTypes.STRING,
  inventory_quantity: {
    type: DataTypes.INTEGER,
    defaultValue: 0
  },
  weight: DataTypes.DECIMAL(8, 2),
  option1: DataTypes.STRING,
  option2: DataTypes.STRING,
  option3: DataTypes.STRING
}, {
  sequelize,
  tableName: 'product_variants',
  timestamps: true,
  createdAt: 'created_at',
  updatedAt: false
});

InventoryLog.init({
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  product_id: {
    type: DataTypes.INTEGER,
    references: {
      model: Product,
      key: 'id'
    }
  },
  variant_id: {
    type: DataTypes.INTEGER,
    references: {
      model: ProductVariant,
      key: 'id'
    }
  },
  quantity_change: {
    type: DataTypes.INTEGER,
    allowNull: false
  },
  reason: DataTypes.STRING,
  reference_id: DataTypes.INTEGER,
  notes: DataTypes.TEXT
}, {
  sequelize,
  tableName: 'inventory_logs',
  timestamps: true,
  createdAt: 'created_at',
  updatedAt: false
});

// Define associations
Customer.hasMany(Transaction, { foreignKey: 'customer_id' });
Transaction.belongsTo(Customer, { foreignKey: 'customer_id' });
Transaction.hasMany(Dispute, { foreignKey: 'transaction_id' });
Dispute.belongsTo(Transaction, { foreignKey: 'transaction_id' });

// Product variant associations
Product.hasMany(ProductVariant, { foreignKey: 'product_id' });
ProductVariant.belongsTo(Product, { foreignKey: 'product_id' });

// Inventory log associations
Product.hasMany(InventoryLog, { foreignKey: 'product_id' });
InventoryLog.belongsTo(Product, { foreignKey: 'product_id' });
ProductVariant.hasMany(InventoryLog, { foreignKey: 'variant_id' });
InventoryLog.belongsTo(ProductVariant, { foreignKey: 'variant_id' });

// API Routes

// Products Routes
app.get('/api/products', async (req: Request, res: Response) => {
  try {
    const products = await Product.findAll({
      where: { status: 'active' }
    });
    res.json(products);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

app.post('/api/products', async (req: Request, res: Response) => {
  try {
    // Clean up the request data
    const productData = { ...req.body };
    
    // If SKU is empty string, set it to null to avoid unique constraint issues
    if (productData.sku === '') {
      productData.sku = null;
    }
    
    // Ensure required fields are present
    if (!productData.title || !productData.price) {
      return res.status(400).json({ error: 'Title and price are required' });
    }
    
    console.log('Creating product with data:', productData);
    const product = await Product.create(productData);
    res.json(product);
  } catch (error) {
    console.error('Product creation error:', error);
    res.status(400).json({ error: (error as Error).message });
  }
});

app.get('/api/products/:id', async (req: Request, res: Response) => {
  try {
    const product = await Product.findByPk(req.params.id);
    if (!product) {
      return res.status(404).json({ error: 'Product not found' });
    }
    res.json(product);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

// Customers Routes
app.get('/api/customers', async (req: Request, res: Response) => {
  try {
    const customers = await Customer.findAll();
    res.json(customers);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

app.post('/api/customers', async (req: Request, res: Response) => {
  try {
    const customer = await Customer.create(req.body);
    res.json(customer);
  } catch (error) {
    res.status(400).json({ error: (error as Error).message });
  }
});

// Transactions Routes
app.get('/api/transactions', async (req: Request, res: Response) => {
  try {
    const transactions = await Transaction.findAll({
      include: [Customer]
    });
    res.json(transactions);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

app.post('/api/transactions', async (req: Request, res: Response) => {
  try {
    // Generate order number if not provided
    if (!req.body.order_number) {
      req.body.order_number = `ORD-${Date.now()}`;
    }
    
    const transaction = await Transaction.create(req.body);
    res.json(transaction);
  } catch (error) {
    res.status(400).json({ error: (error as Error).message });
  }
});

// Stripe Payment Routes
app.post('/api/create-payment-intent', async (req: Request, res: Response) => {
  try {
    const { amount, currency = 'usd', customer_email, product_id } = req.body;
    
    // Create payment intent with crypto support
    const paymentIntent = await stripe.paymentIntents.create({
      amount: Math.round(amount * 100), // Convert to cents
      currency,
      automatic_payment_methods: {
        enabled: true,
        allow_redirects: 'never' // For better UX
      },
      metadata: {
        product_id: product_id?.toString() || '',
        customer_email: customer_email || ''
      }
    });
    
    res.json({ 
      client_secret: paymentIntent.client_secret,
      payment_intent_id: paymentIntent.id 
    });
  } catch (error) {
    console.error('Stripe payment intent creation failed:', error);
    res.status(400).json({ 
      error: 'Failed to create payment intent',
      details: (error as Error).message 
    });
  }
});

// Confirm payment and create transaction record
app.post('/api/confirm-payment', async (req: Request, res: Response) => {
  try {
    const { payment_intent_id, customer_info, product_id } = req.body;
    
    // Retrieve the payment intent from Stripe
    const paymentIntent = await stripe.paymentIntents.retrieve(payment_intent_id);
    
    if (paymentIntent.status === 'succeeded') {
      // Get product info
      const product = await Product.findByPk(product_id);
      if (!product) {
        return res.status(404).json({ error: 'Product not found' });
      }
      
      // Create or find customer
      let customer = await Customer.findOne({ where: { email: customer_info.email } });
      if (!customer) {
        customer = await Customer.create({
          email: customer_info.email,
          first_name: customer_info.first_name || '',
          last_name: customer_info.last_name || '',
          phone: customer_info.phone || ''
        });
      }
      
      // Create transaction record
      const transaction = await Transaction.create({
        customer_id: customer.id,
        order_number: `ORD-${Date.now()}`,
        status: 'completed',
        payment_status: 'paid',
        fulfillment_status: 'unfulfilled',
        subtotal: product.price,
        tax_amount: 0,
        shipping_amount: 0,
        discount_amount: 0,
        total_amount: product.price,
        payment_method: paymentIntent.payment_method_types[0] || 'card',
        stripe_payment_intent_id: payment_intent_id,
        customer_email: customer_info.email,
        line_items: [{
          product_id: product.id,
          title: product.title,
          price: product.price,
          quantity: 1
        }]
      });
      
      // Update product inventory
      await product.update({
        inventory_quantity: Math.max(0, product.inventory_quantity - 1)
      });
      
      // Update customer totals
      await customer.update({
        total_spent: parseFloat(customer.total_spent.toString()) + parseFloat(product.price.toString()),
        order_count: customer.order_count + 1,
        last_order_date: new Date()
      });
      
      // Refresh customer data to get updated values
      await customer.reload();
      
      // Track the purchase with analytics services
      try {
        const customerData = {
          id: customer.id,
          email: customer.email,
          first_name: customer.first_name || '',
          last_name: customer.last_name || '',
          phone: customer.phone || '',
          total_spent: customer.total_spent,
          order_count: customer.order_count,
          created_at: customer.created_at
        };
        
        const orderData = {
          customer_id: customer.id,
          order_number: transaction.order_number,
          total_amount: product.price,
          line_items: JSON.stringify([{
            item_id: product.id.toString(),
            item_name: product.title,
            quantity: 1,
            price: product.price
          }])
        };
        
        // Track across all enabled services
        await serviceManager.trackPurchase(customerData, orderData);
        console.log('✅ Purchase tracked across analytics services');
        
        // Identify customer for future tracking
        await serviceManager.identifyCustomer(customerData);
        console.log('✅ Customer identified in analytics services');
        
      } catch (analyticsError) {
        console.warn('⚠️ Analytics tracking failed:', (analyticsError as Error).message);
        // Don't fail the payment if analytics fail
      }
      
      res.json({ 
        success: true,
        transaction_id: transaction.id,
        order_number: transaction.order_number
      });
    } else {
      res.status(400).json({ 
        error: 'Payment not successful',
        status: paymentIntent.status 
      });
    }
  } catch (error) {
    console.error('Payment confirmation failed:', error);
    res.status(500).json({ 
      error: 'Failed to confirm payment',
      details: (error as Error).message 
    });
  }
});

// Disputes Routes
app.get('/api/disputes', async (req: Request, res: Response) => {
  try {
    const disputes = await Dispute.findAll({
      include: [Transaction]
    });
    res.json(disputes);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

app.post('/api/disputes', async (req: Request, res: Response) => {
  try {
    const dispute = await Dispute.create(req.body);
    res.json(dispute);
  } catch (error) {
    res.status(400).json({ error: (error as Error).message });
  }
});

// Testing endpoints for integration verification
app.get('/api/test/table-schema/:tableName', async (req: Request, res: Response) => {
  try {
    const { tableName } = req.params;
    const [results] = await sequelize.query(`
      SELECT column_name, data_type, is_nullable, column_default
      FROM information_schema.columns 
      WHERE table_name = '${tableName}' 
      AND table_schema = 'public'
      ORDER BY ordinal_position;
    `);
    
    if (results.length === 0) {
      return res.status(404).json({ error: `Table ${tableName} not found` });
    }
    
    const columns = (results as any[]).map(col => col.column_name);
    res.json({ 
      table: tableName, 
      columns,
      details: results 
    });
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

app.post('/api/test/create-customer', async (req: Request, res: Response) => {
  try {
    const customerData = req.body;
    
    // Add test prefix to email to avoid conflicts
    if (!customerData.email.includes('test')) {
      customerData.email = `test_${Date.now()}_${customerData.email}`;
    }
    
    const customer = await Customer.create(customerData);
    res.json(customer);
  } catch (error) {
    res.status(400).json({ error: (error as Error).message });
  }
});

app.post('/api/test/create-transaction', async (req: Request, res: Response) => {
  try {
    const transactionData = req.body;
    
    // Ensure required fields are present
    if (!transactionData.order_number) {
      transactionData.order_number = `TEST-${Date.now()}`;
    }
    if (!transactionData.subtotal) {
      transactionData.subtotal = transactionData.total_amount;
    }
    
    const transaction = await Transaction.create(transactionData);
    res.json(transaction);
  } catch (error) {
    res.status(400).json({ error: (error as Error).message });
  }
});

app.delete('/api/test/cleanup', async (req: Request, res: Response) => {
  try {
    const { email } = req.body;
    
    if (email && email.includes('test')) {
      // Find customer by email
      const customer = await Customer.findOne({ where: { email } });
      
      if (customer) {
        // Delete associated transactions first (due to foreign key constraints)
        await Transaction.destroy({ where: { customer_id: customer.id } });
        
        // Delete customer
        await Customer.destroy({ where: { email } });
        
        res.json({ message: 'Test data cleaned up successfully' });
      } else {
        res.json({ message: 'No test data found to clean up' });
      }
    } else {
      res.status(400).json({ error: 'Invalid email for cleanup' });
    }
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

app.get('/api/test/health', async (req: Request, res: Response) => {
  try {
    // Test database connection
    await sequelize.authenticate();
    
    // Check if required tables exist
    const tables = ['customers', 'products', 'transactions', 'disputes'];
    const tableChecks = await Promise.all(
      tables.map(async (table) => {
        try {
          const [results] = await sequelize.query(`SELECT 1 FROM ${table} LIMIT 1`);
          return { table, exists: true };
        } catch {
          return { table, exists: false };
        }
      })
    );
    
    res.json({
      status: 'healthy',
      database: 'connected',
      tables: tableChecks,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ 
      status: 'unhealthy',
      error: (error as Error).message,
      timestamp: new Date().toISOString()
    });
  }
});

// Get customer by ID for testing
app.get('/api/customers/:id', async (req: Request, res: Response) => {
  try {
    const customer = await Customer.findByPk(req.params.id);
    if (!customer) {
      return res.status(404).json({ error: 'Customer not found' });
    }
    res.json(customer);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

// Get transaction by ID for testing
app.get('/api/transactions/:id', async (req: Request, res: Response) => {
  try {
    const transaction = await Transaction.findByPk(req.params.id);
    if (!transaction) {
      return res.status(404).json({ error: 'Transaction not found' });
    }
    res.json(transaction);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

// Initialize database and start server
const PORT = process.env.PORT || 3000;

async function startServer() {
  try {
    await sequelize.authenticate();
    console.log('Database connection established successfully.');
    
    // Sync database (create tables)
    await sequelize.sync({ alter: true });
    console.log('Database synchronized.');
    
    app.listen(PORT, () => {
      console.log(`Server running on port ${PORT}`);
    });
  } catch (error) {
    console.error('Unable to start server:', error);
  }
}

startServer();

export { app, sequelize, Customer, Product, Transaction, Dispute, ProductVariant, InventoryLog };
