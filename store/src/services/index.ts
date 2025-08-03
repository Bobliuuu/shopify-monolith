// Export all services
export { StripeService, PaymentForm } from './StripeService';
export { GoogleAnalyticsService, ga4 } from './GoogleAnalyticsService';
export { CustomerIOService, customerio } from './CustomerIOService';

// Import services for internal use
import { StripeService } from './StripeService';
import { GoogleAnalyticsService } from './GoogleAnalyticsService';
import { CustomerIOService } from './CustomerIOService';

// Re-export types for convenience
export type {
  Product,
  Customer,
  PaymentFormProps
} from './StripeService';

// Common interfaces used across services
export interface OrderData {
  customer_id?: number;
  order_number: string;
  total_amount: number;
  line_items?: string;
}

export interface CustomerData {
  id: number;
  email: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  total_spent?: number;
  order_count?: number;
  created_at?: Date;
  [key: string]: any;
}

export interface EventData {
  [key: string]: any;
}

// Service configuration interfaces
export interface StripeConfig {
  publishableKey: string;
  apiUrl?: string;
}

export interface GAConfig {
  measurementId: string;
  apiSecret: string;
  debug?: boolean;
}

export interface CustomerIOConfig {
  siteId: string;
  apiKey: string;
  trackingUrl?: string;
  debug?: boolean;
}

// Unified service manager for easier integration
export class ServiceManager {
  private static instance: ServiceManager;
  
  private stripeService?: StripeService;
  private gaService?: GoogleAnalyticsService;
  private customerIOService?: CustomerIOService;

  static getInstance(): ServiceManager {
    if (!ServiceManager.instance) {
      ServiceManager.instance = new ServiceManager();
    }
    return ServiceManager.instance;
  }

  /**
   * Initialize all services from environment variables
   */
  initFromEnvironment(): void {
    try {
      this.gaService = GoogleAnalyticsService.fromEnvironment();
    } catch (error) {
      console.warn('Google Analytics not initialized:', (error as Error).message);
    }

    try {
      this.customerIOService = CustomerIOService.fromEnvironment();
    } catch (error) {
      console.warn('Customer.io not initialized:', (error as Error).message);
    }
  }

  /**
   * Initialize Stripe service
   */
  initStripe(config: StripeConfig): void {
    this.stripeService = StripeService.getInstance(config);
  }

  /**
   * Initialize Google Analytics service
   */
  initGA(config: GAConfig): void {
    this.gaService = GoogleAnalyticsService.getInstance(config);
  }

  /**
   * Initialize Customer.io service
   */
  initCustomerIO(config: CustomerIOConfig): void {
    this.customerIOService = CustomerIOService.getInstance(config);
  }

  /**
   * Track a purchase across all enabled services
   */
  async trackPurchase(customerData: CustomerData, orderData: OrderData, clientId?: string): Promise<void> {
    const promises: Promise<void>[] = [];

    if (this.gaService) {
      promises.push(this.gaService.trackPurchase(orderData, clientId));
    }

    if (this.customerIOService) {
      promises.push(this.customerIOService.trackPurchase(customerData, orderData));
    }

    await Promise.allSettled(promises);
  }

  /**
   * Track a custom event across all enabled services
   */
  async trackEvent(eventName: string, eventData: EventData, customerId?: number, clientId?: string): Promise<void> {
    const promises: Promise<void>[] = [];

    if (this.gaService) {
      promises.push(this.gaService.trackEvent(eventName, eventData, clientId));
    }

    if (this.customerIOService && customerId) {
      promises.push(this.customerIOService.trackEvent(customerId, eventName, eventData));
    }

    await Promise.allSettled(promises);
  }

  /**
   * Identify a customer across all enabled services
   */
  async identifyCustomer(customerData: CustomerData): Promise<void> {
    const promises: Promise<void>[] = [];

    if (this.customerIOService) {
      promises.push(this.customerIOService.identifyCustomer(customerData));
    }

    if (this.gaService) {
      promises.push(this.gaService.setUserProperties({
        user_id: customerData.id.toString(),
        customer_lifetime_value: customerData.total_spent,
        user_category: customerData.order_count && customerData.order_count > 5 ? 'vip' : 'regular'
      }));
    }

    await Promise.allSettled(promises);
  }

  /**
   * Track page view across all enabled services
   */
  async trackPageView(pageData: {
    page_title: string;
    page_location: string;
    page_referrer?: string;
  }, customerId?: number, clientId?: string): Promise<void> {
    const promises: Promise<void>[] = [];

    if (this.gaService) {
      promises.push(this.gaService.trackPageView(pageData, clientId));
    }

    if (this.customerIOService && customerId) {
      promises.push(this.customerIOService.trackPageView(customerId, {
        page_url: pageData.page_location,
        page_title: pageData.page_title,
        referrer: pageData.page_referrer
      }));
    }

    await Promise.allSettled(promises);
  }

  // Getters for individual services
  get stripe(): StripeService | undefined {
    return this.stripeService;
  }

  get ga(): GoogleAnalyticsService | undefined {
    return this.gaService;
  }

  get customerIO(): CustomerIOService | undefined {
    return this.customerIOService;
  }
}

// Export default service manager instance
export const services = ServiceManager.getInstance();
