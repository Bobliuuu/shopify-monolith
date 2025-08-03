/**
 * Example usage of all services in the Shopify Monolith store
 * This file demonstrates how to integrate Google Analytics 4, Customer.io, and Stripe
 */

import { 
  services, 
  ServiceManager,
  GoogleAnalyticsService,
  CustomerIOService,
  StripeService,
  type CustomerData,
  type OrderData 
} from './index';

// Example: Initialize all services
export function initializeServices() {
  const serviceManager = ServiceManager.getInstance();
  
  // Initialize from environment variables (recommended)
  serviceManager.initFromEnvironment();
  
  // Or initialize manually with config
  serviceManager.initStripe({
    publishableKey: 'pk_test_A7jK4iCYHL045qgjjfzAfPxu',
    apiUrl: 'http://localhost:3000'
  });

  serviceManager.initGA({
    measurementId: 'G-XXXXXXXXXX',
    apiSecret: 'your-api-secret',
    debug: true
  });

  serviceManager.initCustomerIO({
    siteId: 'your-site-id',
    apiKey: 'your-api-key',
    debug: true
  });
}

// Example: Track a complete purchase flow
export async function handlePurchaseComplete(customerData: CustomerData, orderData: OrderData) {
  try {
    // Track the purchase across all services
    await services.trackPurchase(customerData, orderData);
    
    console.log('Purchase tracked successfully across all services');
  } catch (error) {
    console.error('Error tracking purchase:', error);
  }
}

// Example: Track user interactions
export async function trackUserInteractions() {
  const customerId = 123;
  const clientId = 'user-client-id-123';

  // Track page view
  await services.trackPageView({
    page_title: 'Product Catalog',
    page_location: 'https://yourstore.com/products',
    page_referrer: 'https://google.com'
  }, customerId, clientId);

  // Track custom event
  await services.trackEvent('product_viewed', {
    product_id: 'prod_123',
    product_name: 'Mountain Hiking Boots',
    category: 'footwear',
    price: 129.99
  }, customerId, clientId);
}

// Example: Using individual services
export async function useIndividualServices() {
  // Google Analytics 4
  const ga = GoogleAnalyticsService.fromEnvironment();
  
  await ga.trackAddToCart({
    item_id: 'prod_123',
    item_name: 'Mountain Hiking Boots',
    currency: 'USD',
    value: 129.99,
    quantity: 1
  });

  await ga.trackSearch('hiking boots');
  
  await ga.trackLogin('email');

  // Customer.io
  const customerio = CustomerIOService.fromEnvironment();
  
  await customerio.identifyCustomer({
    id: 123,
    email: 'customer@example.com',
    first_name: 'John',
    last_name: 'Doe',
    total_spent: 299.97,
    order_count: 3
  });

  await customerio.trackProductView(123, {
    product_id: 'prod_123',
    product_name: 'Mountain Hiking Boots',
    product_price: 129.99,
    category: 'footwear'
  });

  await customerio.trackEmailEvent(123, 'opened', {
    campaign_id: 'welcome_series_1',
    email_address: 'customer@example.com',
    subject: 'Welcome to our store!'
  });
}

// Example: E-commerce tracking setup
export function setupEcommerceTracking() {
  // Initialize services
  initializeServices();

  // Track when user lands on the site
  document.addEventListener('DOMContentLoaded', () => {
    services.trackPageView({
      page_title: document.title,
      page_location: window.location.href,
      page_referrer: document.referrer
    });
  });

  // Track product views
  window.addEventListener('product-view', (event: any) => {
    const { productId, productName, price, customerId } = event.detail;
    
    services.trackEvent('view_item', {
      currency: 'USD',
      value: price,
      items: [{
        item_id: productId,
        item_name: productName,
        price: price,
        quantity: 1
      }]
    }, customerId);
  });

  // Track add to cart
  window.addEventListener('add-to-cart', (event: any) => {
    const { productId, productName, price, customerId } = event.detail;
    
    services.ga?.trackAddToCart({
      item_id: productId,
      item_name: productName,
      currency: 'USD',
      value: price,
      quantity: 1
    });

    if (customerId) {
      services.customerIO?.trackEvent(customerId, 'added_to_cart', {
        product_id: productId,
        product_name: productName,
        price: price
      });
    }
  });
}

// Example: Customer lifecycle tracking
export async function trackCustomerLifecycle(customerId: number) {
  const customerIO = services.customerIO;
  
  if (!customerIO) return;

  // Track registration
  await customerIO.trackRegistration({
    id: customerId,
    email: 'newcustomer@example.com',
    first_name: 'New',
    last_name: 'Customer'
  }, 'website');

  // Track first purchase (after some time)
  setTimeout(async () => {
    await customerIO.trackEvent(customerId, 'first_purchase', {
      order_value: 89.99,
      product_category: 'electronics'
    });
  }, 5000);

  // Track subscription to newsletter
  await customerIO.trackEvent(customerId, 'newsletter_subscribed', {
    subscription_source: 'footer_form'
  });
}

// Example: Advanced analytics
export async function advancedAnalytics() {
  const ga = services.ga;
  
  if (!ga) return;

  // Track video engagement
  await ga.trackVideo({
    video_title: 'Product Demo - Hiking Boots',
    video_provider: 'youtube',
    video_duration: 120,
    video_current_time: 60,
    video_percent: 50
  }, 'video_progress');

  // Track user engagement
  await ga.trackEngagement({
    engagement_time_msec: 30000,
    session_id: 'session_123'
  });

  // Set user properties for segmentation
  await ga.setUserProperties({
    user_id: 'user_123',
    customer_lifetime_value: 299.97,
    user_category: 'regular_customer',
    preferred_category: 'outdoor_gear'
  });
}

// Export initialization function for use in main app
export { initializeServices as default };
