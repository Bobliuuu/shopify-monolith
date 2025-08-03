interface CustomerData {
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

interface EventData {
  [key: string]: any;
}

interface OrderData {
  customer_id?: number;
  order_number: string;
  total_amount: number;
  line_items?: string;
}

interface CustomerIOConfig {
  siteId: string;
  apiKey: string;
  trackingUrl?: string;
  debug?: boolean;
}

interface CustomerIOEvent {
  name: string;
  data: EventData;
  timestamp?: number;
}

interface CustomerIOIdentify {
  id: number;
  email: string;
  created_at?: number;
  [key: string]: any;
}

export class CustomerIOService {
  private static instance: CustomerIOService;
  private config: CustomerIOConfig;
  private trackEndpoint: string;

  constructor(config: CustomerIOConfig) {
    this.config = config;
    this.trackEndpoint = config.trackingUrl || 'https://track.customer.io/api/v1';
  }

  static getInstance(config?: CustomerIOConfig): CustomerIOService {
    if (!CustomerIOService.instance) {
      if (!config) {
        throw new Error('CustomerIOService must be initialized with config first');
      }
      CustomerIOService.instance = new CustomerIOService(config);
    }
    return CustomerIOService.instance;
  }

  /**
   * Initialize Customer.io from environment variables
   */
  static fromEnvironment(): CustomerIOService {
    const siteId = process.env.CUSTOMERIO_SITE_ID;
    const apiKey = process.env.CUSTOMERIO_API_KEY;

    if (!siteId || !apiKey) {
      throw new Error('CUSTOMERIO_SITE_ID and CUSTOMERIO_API_KEY environment variables are required');
    }

    return CustomerIOService.getInstance({
      siteId,
      apiKey,
      debug: process.env.NODE_ENV === 'development'
    });
  }

  /**
   * Get authentication headers for Customer.io API
   */
  private getAuthHeaders(): { [key: string]: string } {
    const credentials = Buffer.from(`${this.config.siteId}:${this.config.apiKey}`).toString('base64');
    return {
      'Authorization': `Basic ${credentials}`,
      'Content-Type': 'application/json'
    };
  }

  /**
   * Make authenticated request to Customer.io API
   */
  private async makeRequest(method: string, endpoint: string, data?: any): Promise<any> {
    try {
      const response = await fetch(`${this.trackEndpoint}${endpoint}`, {
        method,
        headers: this.getAuthHeaders(),
        body: data ? JSON.stringify(data) : undefined
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Customer.io API error: ${response.status} ${response.statusText} - ${errorText}`);
      }

      if (this.config.debug) {
        console.log(`Customer.io ${method} ${endpoint} successful`);
      }

      // Customer.io tracking API typically returns empty responses for success
      return response.status === 200 ? await response.json().catch(() => ({})) : {};
    } catch (error) {
      console.error('Customer.io API error:', error);
      if (this.config.debug) {
        console.error('Failed request:', { method, endpoint, data });
      }
      throw error;
    }
  }

  /**
   * Identify a customer in Customer.io
   */
  async identifyCustomer(customerData: CustomerData): Promise<void> {
    const identifyData: CustomerIOIdentify = {
      id: customerData.id,
      email: customerData.email,
      created_at: customerData.created_at ? Math.floor(new Date(customerData.created_at).getTime() / 1000) : Math.floor(Date.now() / 1000)
    };

    // Add optional fields if they exist
    if (customerData.first_name) identifyData.first_name = customerData.first_name;
    if (customerData.last_name) identifyData.last_name = customerData.last_name;
    if (customerData.phone) identifyData.phone = customerData.phone;
    if (customerData.total_spent !== undefined) identifyData.total_spent = customerData.total_spent;
    if (customerData.order_count !== undefined) identifyData.order_count = customerData.order_count;

    // Add any additional custom attributes
    Object.keys(customerData).forEach(key => {
      if (!['id', 'email', 'first_name', 'last_name', 'phone', 'total_spent', 'order_count', 'created_at'].includes(key)) {
        identifyData[key] = customerData[key];
      }
    });

    await this.makeRequest('PUT', `/customers/${customerData.id}`, identifyData);
  }

  /**
   * Track an event for a customer
   */
  async trackEvent(customerId: number, eventName: string, eventData: EventData = {}): Promise<void> {
    const event: CustomerIOEvent = {
      name: eventName,
      data: eventData,
      timestamp: Math.floor(Date.now() / 1000)
    };

    await this.makeRequest('POST', `/customers/${customerId}/events`, event);
  }

  /**
   * Track a purchase event (combines identify and track)
   */
  async trackPurchase(customerData: CustomerData, orderData: OrderData): Promise<void> {
    // First identify the customer
    await this.identifyCustomer(customerData);

    // Then track the purchase event
    const purchaseData = {
      order_number: orderData.order_number,
      total_amount: orderData.total_amount,
      items: orderData.line_items ? JSON.parse(orderData.line_items) : [],
      timestamp: Math.floor(Date.now() / 1000)
    };

    await this.trackEvent(customerData.id, 'purchase', purchaseData);
  }

  /**
   * Track user registration
   */
  async trackRegistration(customerData: CustomerData, source?: string): Promise<void> {
    await this.identifyCustomer(customerData);
    
    const registrationData: EventData = {
      registration_source: source || 'website',
      timestamp: Math.floor(Date.now() / 1000)
    };

    await this.trackEvent(customerData.id, 'registration', registrationData);
  }

  /**
   * Track login event
   */
  async trackLogin(customerId: number, loginData?: EventData): Promise<void> {
    const data = {
      login_time: Math.floor(Date.now() / 1000),
      ...loginData
    };

    await this.trackEvent(customerId, 'login', data);
  }

  /**
   * Track product view
   */
  async trackProductView(customerId: number, productData: {
    product_id: string;
    product_name: string;
    product_price?: number;
    category?: string;
    [key: string]: any;
  }): Promise<void> {
    const data = {
      ...productData,
      timestamp: Math.floor(Date.now() / 1000)
    };

    await this.trackEvent(customerId, 'product_viewed', data);
  }

  /**
   * Track cart abandonment
   */
  async trackCartAbandonment(customerId: number, cartData: {
    cart_value: number;
    items: any[];
    [key: string]: any;
  }): Promise<void> {
    const data = {
      ...cartData,
      timestamp: Math.floor(Date.now() / 1000)
    };

    await this.trackEvent(customerId, 'cart_abandoned', data);
  }

  /**
   * Track email events (opened, clicked, etc.)
   */
  async trackEmailEvent(customerId: number, eventType: 'opened' | 'clicked' | 'bounced' | 'unsubscribed', emailData: {
    campaign_id?: string;
    email_address: string;
    subject?: string;
    [key: string]: any;
  }): Promise<void> {
    const data = {
      ...emailData,
      timestamp: Math.floor(Date.now() / 1000)
    };

    await this.trackEvent(customerId, `email_${eventType}`, data);
  }

  /**
   * Update customer attributes
   */
  async updateCustomer(customerId: number, attributes: { [key: string]: any }): Promise<void> {
    await this.makeRequest('PUT', `/customers/${customerId}`, attributes);
  }

  /**
   * Delete a customer
   */
  async deleteCustomer(customerId: number): Promise<void> {
    await this.makeRequest('DELETE', `/customers/${customerId}`);
  }

  /**
   * Track page view
   */
  async trackPageView(customerId: number, pageData: {
    page_url: string;
    page_title?: string;
    referrer?: string;
    [key: string]: any;
  }): Promise<void> {
    const data = {
      ...pageData,
      timestamp: Math.floor(Date.now() / 1000)
    };

    await this.trackEvent(customerId, 'page_viewed', data);
  }

  /**
   * Track subscription events
   */
  async trackSubscription(customerId: number, subscriptionData: {
    plan_name: string;
    plan_price: number;
    billing_cycle: string;
    status: 'active' | 'canceled' | 'expired' | 'paused';
    [key: string]: any;
  }, action: 'started' | 'canceled' | 'renewed' | 'upgraded' | 'downgraded'): Promise<void> {
    const data = {
      ...subscriptionData,
      timestamp: Math.floor(Date.now() / 1000)
    };

    await this.trackEvent(customerId, `subscription_${action}`, data);
  }

  /**
   * Add customer to a segment
   */
  async addToSegment(customerId: number, segmentId: string): Promise<void> {
    await this.makeRequest('POST', `/customers/${customerId}/segments/${segmentId}`, {});
  }

  /**
   * Remove customer from a segment
   */
  async removeFromSegment(customerId: number, segmentId: string): Promise<void> {
    await this.makeRequest('DELETE', `/customers/${customerId}/segments/${segmentId}`);
  }
}

// Export a default instance for convenience
export const customerio = {
  init: (config: CustomerIOConfig) => CustomerIOService.getInstance(config),
  fromEnv: () => CustomerIOService.fromEnvironment()
};

export default CustomerIOService;
