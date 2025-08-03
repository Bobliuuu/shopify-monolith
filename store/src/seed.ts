import { Customer, Product, Transaction, Dispute, ProductVariant, InventoryLog, sequelize } from './server';

async function seedDatabase(): Promise<void> {
  try {
    console.log('Starting database seeding...');
    
    // Wait for database connection
    await sequelize.authenticate();
    
    // Sync database
    await sequelize.sync({ force: true }); // This will drop and recreate tables
    
    // Create sample products
    const products = await Product.bulkCreate([
      {
        title: 'Alpine Pro Snowboard',
        description: 'Professional grade snowboard perfect for advanced riders. Features carbon fiber construction and responsive edge control.',
        price: 599.99,
        compare_at_price: 799.99,
        sku: 'ALPINE-PRO-001',
        inventory_quantity: 15,
        weight: 3.2,
        vendor: 'Alpine Sports',
        product_type: 'Snowboard',
        tags: ['professional', 'carbon-fiber', 'advanced'],
        handle: 'alpine-pro-snowboard',
        status: 'active'
      },
      {
        title: 'Freestyle Master Board',
        description: 'Perfect for park riding and freestyle tricks. Lightweight and durable with excellent pop.',
        price: 449.99,
        compare_at_price: 549.99,
        sku: 'FREESTYLE-001',
        inventory_quantity: 22,
        weight: 2.8,
        vendor: 'Freestyle Co',
        product_type: 'Snowboard',
        tags: ['freestyle', 'park', 'lightweight'],
        handle: 'freestyle-master-board',
        status: 'active'
      },
      {
        title: 'Beginner Friendly Board',
        description: 'Ideal for beginners learning to snowboard. Forgiving and stable with easy turn initiation.',
        price: 299.99,
        sku: 'BEGINNER-001',
        inventory_quantity: 30,
        weight: 3.0,
        vendor: 'Learn2Ride',
        product_type: 'Snowboard',
        tags: ['beginner', 'stable', 'forgiving'],
        handle: 'beginner-friendly-board',
        status: 'active'
      },
      {
        title: 'Powder Hunter Snowboard',
        description: 'Designed for deep powder days. Wide nose and tapered tail for effortless floating.',
        price: 699.99,
        compare_at_price: 899.99,
        sku: 'POWDER-001',
        inventory_quantity: 8,
        weight: 3.5,
        vendor: 'Mountain Gear',
        product_type: 'Snowboard',
        tags: ['powder', 'deep-snow', 'floating'],
        handle: 'powder-hunter-snowboard',
        status: 'active'
      },
      {
        title: 'All-Mountain Cruiser',
        description: 'Versatile board for all conditions. Great for groomed runs and light powder.',
        price: 519.99,
        sku: 'ALLMTN-001',
        inventory_quantity: 18,
        weight: 3.1,
        vendor: 'Versatile Boards',
        product_type: 'Snowboard',
        tags: ['all-mountain', 'versatile', 'groomed'],
        handle: 'all-mountain-cruiser',
        status: 'active'
      }
    ]);

    console.log(`Created ${products.length} products`);

    // Create sample customers
    const customers = await Customer.bulkCreate([
      {
        email: 'john.doe@email.com',
        first_name: 'John',
        last_name: 'Doe',
        phone: '555-0123',
        total_spent: 599.99,
        order_count: 1
      },
      {
        email: 'jane.smith@email.com', 
        first_name: 'Jane',
        last_name: 'Smith',
        phone: '555-0456',
        total_spent: 449.99,
        order_count: 1
      },
      {
        email: 'mike.wilson@email.com',
        first_name: 'Mike', 
        last_name: 'Wilson',
        phone: '555-0789',
        total_spent: 0,
        order_count: 0
      }
    ]);

    console.log(`Created ${customers.length} customers`);

    // Create sample transactions
    const transactions = await Transaction.bulkCreate([
      {
        customer_id: customers[0].id,
        order_number: 'ORD-2024-001',
        status: 'completed',
        payment_status: 'paid',
        fulfillment_status: 'fulfilled',
        subtotal: 599.99,
        tax_amount: 48.00,
        shipping_amount: 15.00,
        total_amount: 662.99,
        payment_method: 'card',
        customer_email: 'john.doe@email.com',
        line_items: [{
          product_id: products[0].id,
          title: 'Alpine Pro Snowboard',
          quantity: 1,
          price: 599.99
        }] as any,
        shipping_address: {
          first_name: 'John',
          last_name: 'Doe',
          address1: '123 Mountain View Dr',
          city: 'Aspen',
          province: 'CO',
          zip: '81611',
          country: 'US'
        } as any
      },
      {
        customer_id: customers[1].id,
        order_number: 'ORD-2024-002',
        status: 'pending',
        payment_status: 'paid',
        fulfillment_status: 'unfulfilled',
        subtotal: 449.99,
        tax_amount: 36.00,
        shipping_amount: 15.00,
        total_amount: 500.99,
        payment_method: 'card',
        customer_email: 'jane.smith@email.com',
        line_items: [{
          product_id: products[1].id,
          title: 'Freestyle Master Board',
          quantity: 1,
          price: 449.99
        }] as any
      }
    ]);

    console.log(`Created ${transactions.length} transactions`);

    // Create product variants
    const productVariants = await ProductVariant.bulkCreate([
      // Alpine Pro Snowboard variants
      {
        product_id: products[0].id,
        title: '150cm',
        price: 599.99,
        sku: 'ALPINE-PRO-001-150',
        inventory_quantity: 5,
        weight: 3.1,
        option1: '150cm',
        option2: 'Regular',
        option3: 'Black'
      },
      {
        product_id: products[0].id,
        title: '155cm',
        price: 599.99,
        sku: 'ALPINE-PRO-001-155',
        inventory_quantity: 6,
        weight: 3.2,
        option1: '155cm',
        option2: 'Regular',
        option3: 'Black'
      },
      {
        product_id: products[0].id,
        title: '160cm',
        price: 599.99,
        sku: 'ALPINE-PRO-001-160',
        inventory_quantity: 4,
        weight: 3.3,
        option1: '160cm',
        option2: 'Regular',
        option3: 'Black'
      },
      // Freestyle Master Board variants
      {
        product_id: products[1].id,
        title: '145cm - Blue',
        price: 449.99,
        sku: 'FREESTYLE-001-145-BLUE',
        inventory_quantity: 8,
        weight: 2.7,
        option1: '145cm',
        option2: 'Twin',
        option3: 'Blue'
      },
      {
        product_id: products[1].id,
        title: '150cm - Blue',
        price: 449.99,
        sku: 'FREESTYLE-001-150-BLUE',
        inventory_quantity: 9,
        weight: 2.8,
        option1: '150cm',
        option2: 'Twin',
        option3: 'Blue'
      },
      {
        product_id: products[1].id,
        title: '155cm - Red',
        price: 449.99,
        sku: 'FREESTYLE-001-155-RED',
        inventory_quantity: 5,
        weight: 2.9,
        option1: '155cm',
        option2: 'Twin',
        option3: 'Red'
      },
      // Beginner Friendly Board variants
      {
        product_id: products[2].id,
        title: '140cm',
        price: 299.99,
        sku: 'BEGINNER-001-140',
        inventory_quantity: 12,
        weight: 2.9,
        option1: '140cm',
        option2: 'Directional',
        option3: 'Green'
      },
      {
        product_id: products[2].id,
        title: '145cm',
        price: 299.99,
        sku: 'BEGINNER-001-145',
        inventory_quantity: 10,
        weight: 3.0,
        option1: '145cm',
        option2: 'Directional',
        option3: 'Green'
      },
      {
        product_id: products[2].id,
        title: '150cm',
        price: 299.99,
        sku: 'BEGINNER-001-150',
        inventory_quantity: 8,
        weight: 3.1,
        option1: '150cm',
        option2: 'Directional',
        option3: 'Green'
      }
    ]);

    console.log(`Created ${productVariants.length} product variants`);

    // Create inventory logs (tracking inventory changes)
    const inventoryLogs = await InventoryLog.bulkCreate([
      // Initial stock entries
      {
        product_id: products[0].id,
        variant_id: productVariants[0].id,
        quantity_change: 5,
        reason: 'restock',
        notes: 'Initial inventory for Alpine Pro 150cm'
      },
      {
        product_id: products[0].id,
        variant_id: productVariants[1].id,
        quantity_change: 6,
        reason: 'restock',
        notes: 'Initial inventory for Alpine Pro 155cm'
      },
      {
        product_id: products[0].id,
        variant_id: productVariants[2].id,
        quantity_change: 4,
        reason: 'restock',
        notes: 'Initial inventory for Alpine Pro 160cm'
      },
      // Sale transactions
      {
        product_id: products[0].id,
        variant_id: productVariants[1].id,
        quantity_change: -1,
        reason: 'sale',
        reference_id: transactions[0].id,
        notes: 'Sold via order ORD-2024-001'
      },
      {
        product_id: products[1].id,
        variant_id: productVariants[3].id,
        quantity_change: -1,
        reason: 'sale',
        reference_id: transactions[1].id,
        notes: 'Sold via order ORD-2024-002'
      },
      // Inventory adjustments
      {
        product_id: products[2].id,
        quantity_change: -2,
        reason: 'adjustment',
        notes: 'Damaged boards removed from inventory'
      },
      {
        product_id: products[3].id,
        quantity_change: 10,
        reason: 'restock',
        notes: 'New shipment of Powder Hunter boards'
      }
    ]);

    console.log(`Created ${inventoryLogs.length} inventory log entries`);

    // Create a sample dispute
    const disputes = await Dispute.bulkCreate([
      {
        transaction_id: transactions[0].id,
        stripe_dispute_id: 'dp_test_sample123',
        amount: 599.99,
        reason: 'fraudulent',
        status: 'warning_needs_response'
      }
    ]);

    console.log(`Created ${disputes.length} sample disputes`);

    console.log('Database seeding completed successfully!');
    console.log('\nSample data created:');
    console.log(`- ${products.length} products`);
    console.log(`- ${productVariants.length} product variants`);
    console.log(`- ${customers.length} customers`);
    console.log(`- ${transactions.length} transactions`);
    console.log(`- ${inventoryLogs.length} inventory log entries`);
    console.log(`- ${disputes.length} disputes`);
    console.log('\nDatabase schema includes all tables from tables.sql:');
    console.log('✅ customers');
    console.log('✅ products');
    console.log('✅ product_variants');
    console.log('✅ transactions');
    console.log('✅ disputes');
    console.log('✅ inventory_logs');
    
  } catch (error) {
    console.error('Error seeding database:', error);
  } finally {
    process.exit(0);
  }
}

// Run the seeder
seedDatabase();
