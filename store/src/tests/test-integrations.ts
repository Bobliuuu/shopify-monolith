#!/usr/bin/env bun

/**
 * Comprehensive test suite for Shopify Monolith
 * Tests: Server health, database operations, GA4, Customer.io, and service integrations
 * Usage: bun run test
 */

import { 
  DatabaseTester, 
  GA4Tester, 
  CustomerIOTester, 
  generateTestCustomer, 
  generateTestOrder 
} from '../services/testUtils';

// Configuration
const CONFIG = {
  apiUrl: 'http://localhost:3000',
  ga4: {
    measurementId: process.env.GA4_MEASUREMENT_ID || 'G-XXXXXXXXXX',
    apiSecret: process.env.GA4_API_SECRET || 'test-secret'
  },
  customerio: {
    siteId: process.env.CUSTOMERIO_SITE_ID || 'test-site-id',
    apiKey: process.env.CUSTOMERIO_API_KEY || 'test-api-key'
  }
};

async function runHealthChecks(): Promise<boolean> {
  console.log('\n🔍 Running Health Checks...\n');
  
  try {
    // Test server health
    console.log('Testing server connection...');
    const response = await fetch('http://localhost:3000/api/test/health');
    const data = await response.json();
    
    if (data.status === 'healthy') {
      console.log('✅ Server is healthy');
      console.log('✅ Database is connected');
      
      data.tables.forEach((table: any) => {
        console.log(`${table.exists ? '✅' : '❌'} Table ${table.table}: ${table.exists ? 'exists' : 'missing'}`);
      });
      
      return true;
    } else {
      console.log('❌ Server health check failed:', data.error);
      return false;
    }
  } catch (error) {
    console.error('❌ Could not connect to server:', error);
    console.log('💡 Make sure the server is running on http://localhost:3000');
    return false;
  }
}

async function runDatabaseTests(): Promise<boolean> {
  console.log('\n🗄️  Testing Database Schema and Population...\n');
  
  const dbTester = new DatabaseTester(CONFIG.apiUrl);
  let allPassed = true;

  try {
    // Test database schema
    console.log('Testing database schema...');
    const schemaResult = await dbTester.testDatabaseSchema();
    
    if (schemaResult.success) {
      console.log('✅ Database schema validation passed');
      Object.entries(schemaResult.tables).forEach(([table, info]) => {
        if (info.exists) {
          console.log(`  ✅ ${table}: ${info.columns?.length || 0} columns`);
        } else {
          console.log(`  ❌ ${table}: Missing`);
        }
      });
    } else {
      console.log('❌ Database schema validation failed:');
      schemaResult.errors.forEach(error => console.log(`  - ${error}`));
      allPassed = false;
    }

    // Test customer population
    console.log('\nTesting customer data population...');
    const testCustomer = generateTestCustomer();
    const customerResult = await dbTester.testCustomerPopulation(testCustomer);
    
    if (customerResult.success) {
      console.log('✅ Customer data population test passed');
      console.log(`  Customer ID: ${customerResult.customer?.id}`);
      console.log(`  Email: ${customerResult.customer?.email}`);
    } else {
      console.log('❌ Customer data population test failed:');
      customerResult.errors.forEach(error => console.log(`  - ${error}`));
      allPassed = false;
    }

    // Test transaction population
    if (customerResult.customer) {
      console.log('\nTesting transaction data population...');
      const testOrder = generateTestOrder(customerResult.customer.id);
      const transactionResult = await dbTester.testTransactionPopulation(testOrder, customerResult.customer.id);
      
      if (transactionResult.success) {
        console.log('✅ Transaction data population test passed');
        console.log(`  Order Number: ${transactionResult.transaction?.order_number}`);
        console.log(`  Total Amount: $${transactionResult.transaction?.total_amount}`);
      } else {
        console.log('❌ Transaction data population test failed:');
        transactionResult.errors.forEach(error => console.log(`  - ${error}`));
        allPassed = false;
      }
    }

    // Cleanup test data
    await dbTester.cleanupTestData(testCustomer.email);
    console.log('🧹 Test data cleaned up');

  } catch (error) {
    console.error('❌ Database testing error:', error);
    allPassed = false;
  }

  return allPassed;
}

async function runGA4Tests(): Promise<boolean> {
  console.log('\n📊 Testing Google Analytics 4 Integration...\n');
  
  if (!CONFIG.ga4.measurementId || CONFIG.ga4.measurementId === 'G-XXXXXXXXXX') {
    console.log('⚠️  GA4_MEASUREMENT_ID not configured - skipping GA4 tests');
    return true;
  }

  try {
    const ga4Tester = new GA4Tester(CONFIG.ga4);
    const results = await ga4Tester.runAllTests();
    
    if (results.success) {
      console.log('✅ All GA4 tests passed');
    } else {
      console.log('❌ Some GA4 tests failed:');
      Object.entries(results.results).forEach(([test, result]) => {
        if (!result.success) {
          console.log(`  - ${test}: ${result.error}`);
        }
      });
    }
    
    return results.success;
  } catch (error) {
    console.error('❌ GA4 testing error:', error);
    return false;
  }
}

async function runCustomerIOTests(): Promise<boolean> {
  console.log('\n📧 Testing Customer.io Integration...\n');
  
  if (!CONFIG.customerio.siteId || CONFIG.customerio.siteId === 'test-site-id') {
    console.log('⚠️  CUSTOMERIO_SITE_ID not configured - skipping Customer.io tests');
    return true;
  }

  try {
    const customerIOTester = new CustomerIOTester(CONFIG.customerio);
    const results = await customerIOTester.runAllTests();
    
    if (results.success) {
      console.log('✅ All Customer.io tests passed');
    } else {
      console.log('❌ Some Customer.io tests failed:');
      Object.entries(results.results).forEach(([test, result]) => {
        if (!result.success) {
          console.log(`  - ${test}: ${result.error}`);
        }
      });
    }
    
    return results.success;
  } catch (error) {
    console.error('❌ Customer.io testing error:', error);
    return false;
  }
}

async function runIntegrationTests(): Promise<boolean> {
  console.log('\n🔗 Testing Service Integration...\n');
  
  // Test if services work together
  try {
    const { services, ServiceManager } = await import('../services/index');
    
    const serviceManager = ServiceManager.getInstance();
    serviceManager.initFromEnvironment();
    
    // Test unified tracking
    const testCustomer = generateTestCustomer();
    const testOrder = generateTestOrder(testCustomer.id);
    
    console.log('Testing unified purchase tracking...');
    await services.trackPurchase(testCustomer, testOrder);
    console.log('✅ Unified purchase tracking successful');
    
    console.log('Testing unified event tracking...');
    await services.trackEvent('test_integration_event', {
      test_property: 'integration_test',
      timestamp: Date.now()
    }, testCustomer.id);
    console.log('✅ Unified event tracking successful');
    
    console.log('Testing customer identification...');
    await services.identifyCustomer(testCustomer);
    console.log('✅ Customer identification successful');
    
    return true;
  } catch (error) {
    console.error('❌ Integration testing error:', error);
    return false;
  }
}

function printEnvironmentStatus(): void {
  console.log('\n🔧 Environment Configuration:\n');
  
  const envVars = [
    { name: 'GA4_MEASUREMENT_ID', value: process.env.GA4_MEASUREMENT_ID, required: false },
    { name: 'GA4_API_SECRET', value: process.env.GA4_API_SECRET, required: false },
    { name: 'CUSTOMERIO_SITE_ID', value: process.env.CUSTOMERIO_SITE_ID, required: false },
    { name: 'CUSTOMERIO_API_KEY', value: process.env.CUSTOMERIO_API_KEY, required: false },
    { name: 'DB_NAME', value: process.env.DB_NAME, required: true },
    { name: 'DB_USER', value: process.env.DB_USER, required: true },
    { name: 'DB_HOST', value: process.env.DB_HOST, required: true }
  ];
  
  envVars.forEach(env => {
    const status = env.value ? '✅' : (env.required ? '❌' : '⚠️');
    const display = env.value ? 
      (env.name.includes('SECRET') || env.name.includes('KEY') ? '***' : env.value) : 
      'Not set';
    console.log(`${status} ${env.name}: ${display}`);
  });
}

async function main(): Promise<void> {
  console.log('🚀 Starting Comprehensive Integration Tests for Shopify Monolith\n');
  
  // First run health checks
  const serverHealthy = await runHealthChecks();
  if (!serverHealthy) {
    console.log('\n💥 Server health check failed - cannot proceed with tests');
    process.exit(1);
  }
  
  printEnvironmentStatus();
  
  const results = {
    database: await runDatabaseTests(),
    ga4: await runGA4Tests(),
    customerio: await runCustomerIOTests(),
    integration: await runIntegrationTests()
  };
  
  console.log('\n📊 Test Results Summary:\n');
  Object.entries(results).forEach(([test, passed]) => {
    console.log(`${passed ? '✅' : '❌'} ${test.toUpperCase()}: ${passed ? 'PASSED' : 'FAILED'}`);
  });
  
  const allPassed = Object.values(results).every(Boolean);
  console.log(`\n${allPassed ? '🎉' : '💥'} Overall: ${allPassed ? 'ALL TESTS PASSED' : 'SOME TESTS FAILED'}\n`);
  
  if (!allPassed) {
    console.log('💡 Tips for fixing failed tests:');
    if (!results.database) {
      console.log('  - Ensure PostgreSQL is running and accessible');
      console.log('  - Check database connection settings');
      console.log('  - Run database migrations/setup');
    }
    if (!results.ga4) {
      console.log('  - Set GA4_MEASUREMENT_ID and GA4_API_SECRET environment variables');
      console.log('  - Verify GA4 credentials are correct');
    }
    if (!results.customerio) {
      console.log('  - Set CUSTOMERIO_SITE_ID and CUSTOMERIO_API_KEY environment variables');
      console.log('  - Verify Customer.io credentials are correct');
    }
    console.log('');
  }
  
  process.exit(allPassed ? 0 : 1);
}

// Run the tests
main().catch(error => {
  console.error('💥 Fatal error:', error);
  process.exit(1);
});
