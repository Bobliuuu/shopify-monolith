/**
 * Test utilities for GA4, Customer.io, and database verification
 */

import { 
  GoogleAnalyticsService, 
  CustomerIOService, 
  ServiceManager,
  type CustomerData,
  type OrderData 
} from './index';

// Test data generators
export const generateTestCustomer = (id: number = Math.floor(Math.random() * 1000)): CustomerData => ({
  id,
  email: `test${id}@example.com`,
  first_name: 'Test',
  last_name: 'User',
  phone: '+1234567890',
  total_spent: 299.97,
  order_count: 3,
  created_at: new Date()
});

export const generateTestOrder = (customerId: number = 123): OrderData => ({
  customer_id: customerId,
  order_number: `TEST-${Date.now()}`,
  total_amount: 99.99,
  line_items: JSON.stringify([
    {
      item_id: 'test-product-1',
      item_name: 'Test Product',
      quantity: 1,
      price: 99.99
    }
  ])
});

// Database testing utilities
export class DatabaseTester {
  private apiUrl: string;

  constructor(apiUrl: string = 'http://localhost:3000') {
    this.apiUrl = apiUrl;
  }

  /**
   * Test if all required tables exist and have correct structure
   */
  async testDatabaseSchema(): Promise<{
    success: boolean;
    tables: { [key: string]: { exists: boolean; columns?: string[] } };
    errors: string[];
  }> {
    const requiredTables = ['customers', 'products', 'transactions', 'disputes', 'product_variants', 'inventory_logs'];
    const result = {
      success: true,
      tables: {} as { [key: string]: { exists: boolean; columns?: string[] } },
      errors: [] as string[]
    };

    for (const table of requiredTables) {
      try {
        const response = await fetch(`${this.apiUrl}/api/test/table-schema/${table}`);
        if (response.ok) {
          const data = await response.json();
          result.tables[table] = { exists: true, columns: data.columns };
        } else {
          result.tables[table] = { exists: false };
          result.errors.push(`Table ${table} does not exist or is not accessible`);
          result.success = false;
        }
      } catch (error) {
        result.tables[table] = { exists: false };
        result.errors.push(`Error checking table ${table}: ${error}`);
        result.success = false;
      }
    }

    return result;
  }

  /**
   * Test if customer data is being populated correctly
   */
  async testCustomerPopulation(testCustomer: CustomerData): Promise<{
    success: boolean;
    customer?: any;
    errors: string[];
  }> {
    try {
      // Create a test customer
      const createResponse = await fetch(`${this.apiUrl}/api/test/create-customer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testCustomer)
      });

      if (!createResponse.ok) {
        return { success: false, errors: ['Failed to create test customer'] };
      }

      const createdCustomer = await createResponse.json();

      // Verify the customer exists and has correct data
      const fetchResponse = await fetch(`${this.apiUrl}/api/customers/${createdCustomer.id}`);
      if (!fetchResponse.ok) {
        return { success: false, errors: ['Failed to fetch created customer'] };
      }

      const fetchedCustomer = await fetchResponse.json();

      // Validate required fields
      const errors: string[] = [];
      if (fetchedCustomer.email !== testCustomer.email) errors.push('Email mismatch');
      if (fetchedCustomer.first_name !== testCustomer.first_name) errors.push('First name mismatch');
      if (fetchedCustomer.last_name !== testCustomer.last_name) errors.push('Last name mismatch');
      if (!fetchedCustomer.created_at) errors.push('Missing created_at timestamp');

      return {
        success: errors.length === 0,
        customer: fetchedCustomer,
        errors
      };
    } catch (error) {
      return { success: false, errors: [`Database test error: ${error}`] };
    }
  }

  /**
   * Test if transaction data is being populated correctly
   */
  async testTransactionPopulation(testOrder: OrderData, customerId: number): Promise<{
    success: boolean;
    transaction?: any;
    errors: string[];
  }> {
    try {
      const createResponse = await fetch(`${this.apiUrl}/api/test/create-transaction`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...testOrder, customer_id: customerId })
      });

      if (!createResponse.ok) {
        return { success: false, errors: ['Failed to create test transaction'] };
      }

      const createdTransaction = await createResponse.json();

      // Verify the transaction exists and has correct data
      const fetchResponse = await fetch(`${this.apiUrl}/api/transactions/${createdTransaction.id}`);
      if (!fetchResponse.ok) {
        return { success: false, errors: ['Failed to fetch created transaction'] };
      }

      const fetchedTransaction = await fetchResponse.json();

      // Validate required fields
      const errors: string[] = [];
      if (fetchedTransaction.order_number !== testOrder.order_number) errors.push('Order number mismatch');
      if (parseFloat(fetchedTransaction.total_amount) !== testOrder.total_amount) errors.push('Total amount mismatch');
      if (fetchedTransaction.customer_id !== customerId) errors.push('Customer ID mismatch');
      if (!fetchedTransaction.created_at) errors.push('Missing created_at timestamp');

      return {
        success: errors.length === 0,
        transaction: fetchedTransaction,
        errors
      };
    } catch (error) {
      return { success: false, errors: [`Transaction test error: ${error}`] };
    }
  }

  /**
   * Clean up test data
   */
  async cleanupTestData(customerEmail: string): Promise<void> {
    try {
      await fetch(`${this.apiUrl}/api/test/cleanup`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: customerEmail })
      });
    } catch (error) {
      console.error('Cleanup error:', error);
    }
  }
}

// GA4 testing utilities
export class GA4Tester {
  private service: GoogleAnalyticsService;
  private testClientId: string;

  constructor(config: { measurementId: string; apiSecret: string }) {
    this.service = GoogleAnalyticsService.getInstance({ ...config, debug: true });
    this.testClientId = `test_${Date.now()}`;
  }

  /**
   * Test all GA4 tracking methods
   */
  async runAllTests(): Promise<{
    success: boolean;
    results: { [key: string]: { success: boolean; error?: string } };
  }> {
    const tests = [
      { name: 'trackPurchase', test: () => this.testPurchaseTracking() },
      { name: 'trackPageView', test: () => this.testPageViewTracking() },
      { name: 'trackAddToCart', test: () => this.testAddToCartTracking() },
      { name: 'trackCustomEvent', test: () => this.testCustomEventTracking() },
      { name: 'trackLogin', test: () => this.testLoginTracking() },
      { name: 'trackSearch', test: () => this.testSearchTracking() }
    ];

    const results: { [key: string]: { success: boolean; error?: string } } = {};
    let overallSuccess = true;

    for (const test of tests) {
      try {
        await test.test();
        results[test.name] = { success: true };
        console.log(`✅ GA4 ${test.name} test passed`);
      } catch (error) {
        results[test.name] = { success: false, error: String(error) };
        console.error(`❌ GA4 ${test.name} test failed:`, error);
        overallSuccess = false;
      }
    }

    return { success: overallSuccess, results };
  }

  private async testPurchaseTracking(): Promise<void> {
    const testOrder = generateTestOrder();
    await this.service.trackPurchase(testOrder, this.testClientId);
  }

  private async testPageViewTracking(): Promise<void> {
    await this.service.trackPageView({
      page_title: 'Test Page',
      page_location: 'https://test.com/test',
      page_referrer: 'https://google.com'
    }, this.testClientId);
  }

  private async testAddToCartTracking(): Promise<void> {
    await this.service.trackAddToCart({
      item_id: 'test-product',
      item_name: 'Test Product',
      currency: 'USD',
      value: 99.99,
      quantity: 1
    }, this.testClientId);
  }

  private async testCustomEventTracking(): Promise<void> {
    await this.service.trackEvent('test_event', {
      custom_parameter: 'test_value',
      test_number: 123
    }, this.testClientId);
  }

  private async testLoginTracking(): Promise<void> {
    await this.service.trackLogin('email', this.testClientId);
  }

  private async testSearchTracking(): Promise<void> {
    await this.service.trackSearch('test search term', this.testClientId);
  }
}

// Customer.io testing utilities
export class CustomerIOTester {
  private service: CustomerIOService;
  private testCustomerId: number;

  constructor(config: { siteId: string; apiKey: string }) {
    this.service = CustomerIOService.getInstance({ ...config, debug: true });
    this.testCustomerId = Math.floor(Math.random() * 1000000) + 1000;
  }

  /**
   * Test all Customer.io tracking methods
   */
  async runAllTests(): Promise<{
    success: boolean;
    results: { [key: string]: { success: boolean; error?: string } };
  }> {
    const tests = [
      { name: 'identifyCustomer', test: () => this.testCustomerIdentification() },
      { name: 'trackEvent', test: () => this.testEventTracking() },
      { name: 'trackPurchase', test: () => this.testPurchaseTracking() },
      { name: 'trackProductView', test: () => this.testProductViewTracking() },
      { name: 'trackPageView', test: () => this.testPageViewTracking() },
      { name: 'trackLogin', test: () => this.testLoginTracking() }
    ];

    const results: { [key: string]: { success: boolean; error?: string } } = {};
    let overallSuccess = true;

    for (const test of tests) {
      try {
        await test.test();
        results[test.name] = { success: true };
        console.log(`✅ Customer.io ${test.name} test passed`);
      } catch (error) {
        results[test.name] = { success: false, error: String(error) };
        console.error(`❌ Customer.io ${test.name} test failed:`, error);
        overallSuccess = false;
      }
    }

    return { success: overallSuccess, results };
  }

  private async testCustomerIdentification(): Promise<void> {
    const testCustomer = generateTestCustomer(this.testCustomerId);
    await this.service.identifyCustomer(testCustomer);
  }

  private async testEventTracking(): Promise<void> {
    await this.service.trackEvent(this.testCustomerId, 'test_event', {
      test_property: 'test_value',
      test_number: 123
    });
  }

  private async testPurchaseTracking(): Promise<void> {
    const testCustomer = generateTestCustomer(this.testCustomerId);
    const testOrder = generateTestOrder(this.testCustomerId);
    await this.service.trackPurchase(testCustomer, testOrder);
  }

  private async testProductViewTracking(): Promise<void> {
    await this.service.trackProductView(this.testCustomerId, {
      product_id: 'test-product',
      product_name: 'Test Product',
      product_price: 99.99,
      category: 'test'
    });
  }

  private async testPageViewTracking(): Promise<void> {
    await this.service.trackPageView(this.testCustomerId, {
      page_url: 'https://test.com/test',
      page_title: 'Test Page',
      referrer: 'https://google.com'
    });
  }

  private async testLoginTracking(): Promise<void> {
    await this.service.trackLogin(this.testCustomerId, {
      login_method: 'email',
      login_time: Math.floor(Date.now() / 1000)
    });
  }
}

export { GoogleAnalyticsService, CustomerIOService };
