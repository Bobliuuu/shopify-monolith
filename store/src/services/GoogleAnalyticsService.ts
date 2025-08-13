interface OrderData {
  customer_id?: number;
  order_number: string;
  total_amount: number;
  line_items?: string;
}

interface EventData {
  [key: string]: any;
}

interface GAConfig {
  measurementId: string;
  apiSecret: string;
  debug?: boolean;
}

interface GAEvent {
  name: string;
  params: {
    [key: string]: any;
  };
}

interface GAPayload {
  client_id: string;
  events: GAEvent[];
}

export class GoogleAnalyticsService {
  private static instance: GoogleAnalyticsService;
  private config: GAConfig;
  private endpoint: string;

  constructor(config: GAConfig) {
    this.config = config;
    this.endpoint = 'https://www.google-analytics.com/mp/collect';
  }

  static getInstance(config?: GAConfig): GoogleAnalyticsService {
    if (!GoogleAnalyticsService.instance) {
      if (!config) {
        throw new Error('GoogleAnalyticsService must be initialized with config first');
      }
      GoogleAnalyticsService.instance = new GoogleAnalyticsService(config);
    }
    return GoogleAnalyticsService.instance;
  }

  /**
   * Initialize Google Analytics from environment variables
   */
  static fromEnvironment(): GoogleAnalyticsService {
    const measurementId = process.env.GA4_MEASUREMENT_ID;
    const apiSecret = process.env.GA4_API_SECRET;

    if (!measurementId || !apiSecret) {
      throw new Error('GA4_MEASUREMENT_ID and GA4_API_SECRET environment variables are required');
    }

    return GoogleAnalyticsService.getInstance({
      measurementId,
      apiSecret,
      debug: process.env.NODE_ENV === 'development'
    });
  }

  /**
   * Generate a client ID for anonymous users
   */
  private generateClientId(): string {
    return Math.random().toString(36).substring(2) + Date.now().toString(36);
  }

  /**
   * Send event to Google Analytics
   */
  private async sendEvent(payload: GAPayload): Promise<void> {
    try {
      const url = `${this.endpoint}?measurement_id=${this.config.measurementId}&api_secret=${this.config.apiSecret}`;
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`GA4 API error: ${response.status} ${response.statusText}`);
      }

      if (this.config.debug) {
        console.log('GA4 event sent successfully:', payload);
      }
    } catch (error) {
      console.error('GA4 tracking error:', error);
      if (this.config.debug) {
        console.error('Failed payload:', payload);
      }
      throw error;
    }
  }

  /**
   * Track a purchase event
   */
  async trackPurchase(orderData: OrderData, clientId?: string): Promise<void> {
    const payload: GAPayload = {
      client_id: clientId || orderData.customer_id?.toString() || this.generateClientId(),
      events: [{
        name: 'purchase',
        params: {
          transaction_id: orderData.order_number,
          value: parseFloat(orderData.total_amount.toString()),
          currency: 'USD',
          items: orderData.line_items ? JSON.parse(orderData.line_items) : []
        }
      }]
    };

    await this.sendEvent(payload);
  }

  /**
   * Track an add to cart event
   */
  async trackAddToCart(productData: {
    item_id: string;
    item_name: string;
    currency: string;
    value: number;
    quantity?: number;
  }, clientId?: string): Promise<void> {
    const payload: GAPayload = {
      client_id: clientId || this.generateClientId(),
      events: [{
        name: 'add_to_cart',
        params: {
          currency: productData.currency,
          value: productData.value,
          items: [{
            item_id: productData.item_id,
            item_name: productData.item_name,
            quantity: productData.quantity || 1,
            price: productData.value
          }]
        }
      }]
    };

    await this.sendEvent(payload);
  }

  /**
   * Track a page view event
   */
  async trackPageView(pageData: {
    page_title: string;
    page_location: string;
    page_referrer?: string;
  }, clientId?: string): Promise<void> {
    const payload: GAPayload = {
      client_id: clientId || this.generateClientId(),
      events: [{
        name: 'page_view',
        params: {
          page_title: pageData.page_title,
          page_location: pageData.page_location,
          page_referrer: pageData.page_referrer
        }
      }]
    };

    await this.sendEvent(payload);
  }

  /**
   * Track a custom event
   */
  async trackEvent(eventName: string, parameters: EventData, clientId?: string): Promise<void> {
    const payload: GAPayload = {
      client_id: clientId || parameters.client_id || this.generateClientId(),
      events: [{
        name: eventName,
        params: parameters
      }]
    };

    await this.sendEvent(payload);
  }

  /**
   * Track user engagement events
   */
  async trackEngagement(engagementData: {
    engagement_time_msec?: number;
    session_id?: string;
    page_title?: string;
  }, clientId?: string): Promise<void> {
    const payload: GAPayload = {
      client_id: clientId || this.generateClientId(),
      events: [{
        name: 'user_engagement',
        params: {
          engagement_time_msec: engagementData.engagement_time_msec || 100,
          session_id: engagementData.session_id,
          page_title: engagementData.page_title
        }
      }]
    };

    await this.sendEvent(payload);
  }

  /**
   * Track login events
   */
  async trackLogin(method: string = 'email', clientId?: string): Promise<void> {
    const payload: GAPayload = {
      client_id: clientId || this.generateClientId(),
      events: [{
        name: 'login',
        params: {
          method
        }
      }]
    };

    await this.sendEvent(payload);
  }

  /**
   * Track sign up events
   */
  async trackSignUp(method: string = 'email', clientId?: string): Promise<void> {
    const payload: GAPayload = {
      client_id: clientId || this.generateClientId(),
      events: [{
        name: 'sign_up',
        params: {
          method
        }
      }]
    };

    await this.sendEvent(payload);
  }

  /**
   * Track search events
   */
  async trackSearch(searchTerm: string, clientId?: string): Promise<void> {
    const payload: GAPayload = {
      client_id: clientId || this.generateClientId(),
      events: [{
        name: 'search',
        params: {
          search_term: searchTerm
        }
      }]
    };

    await this.sendEvent(payload);
  }

  /**
   * Track video events
   */
  async trackVideo(videoData: {
    video_title: string;
    video_provider?: string;
    video_duration?: number;
    video_current_time?: number;
    video_percent?: number;
  }, action: 'video_start' | 'video_progress' | 'video_complete', clientId?: string): Promise<void> {
    const payload: GAPayload = {
      client_id: clientId || this.generateClientId(),
      events: [{
        name: action,
        params: videoData
      }]
    };

    await this.sendEvent(payload);
  }

  /**
   * Set user properties (for enhanced ecommerce)
   */
  async setUserProperties(userProperties: {
    user_id?: string;
    customer_lifetime_value?: number;
    user_category?: string;
    [key: string]: any;
  }, clientId?: string): Promise<void> {
    const payload: GAPayload = {
      client_id: clientId || this.generateClientId(),
      events: [{
        name: 'user_engagement',
        params: {
          engagement_time_msec: 1
        }
      }]
    };

    // Add user properties to the payload
    (payload as any).user_properties = userProperties;

    await this.sendEvent(payload);
  }
}

// Export a default instance for convenience
export const ga4 = {
  init: (config: GAConfig) => GoogleAnalyticsService.getInstance(config),
  fromEnv: () => GoogleAnalyticsService.fromEnvironment()
};

export default GoogleAnalyticsService;
