import React, { useState, useEffect } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import {
  Elements,
  useStripe,
  useElements,
  PaymentElement
} from '@stripe/react-stripe-js';

// Initialize Stripe with your publishable key
const stripePromise = loadStripe('pk_test_A7jK4iCYHL045qgjjfzAfPxu');

export interface Product {
  id: number;
  title: string;
  description: string;
  price: number;
  inventory_quantity: number;
  status: string;
}

export interface Customer {
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
}

export interface PaymentFormProps {
  product: Product;
  onSuccess: () => void;
  onCancel: () => void;
}

interface StripeConfig {
  publishableKey: string;
  apiUrl?: string;
}

export class StripeService {
  private static instance: StripeService;
  private config: StripeConfig;

  constructor(config: StripeConfig) {
    this.config = config;
  }

  static getInstance(config?: StripeConfig): StripeService {
    if (!StripeService.instance) {
      if (!config) {
        throw new Error('StripeService must be initialized with config first');
      }
      StripeService.instance = new StripeService(config);
    }
    return StripeService.instance;
  }

  async createPaymentIntent(amount: number, currency: string = 'usd', productId?: number): Promise<string> {
    const apiUrl = this.config.apiUrl || 'http://localhost:3000';
    
    try {
      const response = await fetch(`${apiUrl}/api/create-payment-intent`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          amount,
          currency,
          product_id: productId
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create payment intent');
      }

      const data = await response.json();
      return data.client_secret;
    } catch (error) {
      console.error('Error creating payment intent:', error);
      throw error;
    }
  }

  async confirmPayment(paymentIntentId: string, customerInfo: Customer, productId: number): Promise<any> {
    const apiUrl = this.config.apiUrl || 'http://localhost:3000';
    
    try {
      const response = await fetch(`${apiUrl}/api/confirm-payment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          payment_intent_id: paymentIntentId,
          customer_info: customerInfo,
          product_id: productId
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to confirm payment on server');
      }

      return await response.json();
    } catch (error) {
      console.error('Error confirming payment:', error);
      throw error;
    }
  }
}

// Main Payment Form Component
export function PaymentForm({ product, onSuccess, onCancel }: PaymentFormProps) {
  const [clientSecret, setClientSecret] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Create payment intent when component mounts
    const createPaymentIntent = async () => {
      try {
        setLoading(true);
        const stripeService = StripeService.getInstance({
          publishableKey: 'pk_test_A7jK4iCYHL045qgjjfzAfPxu'
        });
        
        const clientSecret = await stripeService.createPaymentIntent(
          product.price,
          'usd',
          product.id
        );
        
        setClientSecret(clientSecret);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    createPaymentIntent();
  }, [product]);

  if (loading) {
    return (
      <div className="payment-modal-overlay" onClick={onCancel}>
        <div className="payment-modal" onClick={(e) => e.stopPropagation()}>
          <button className="modal-close-btn" onClick={onCancel}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </button>
          
          <div className="payment-content">
            <div className="loading-state">
              <div className="loading-spinner"></div>
              <p>Initializing secure payment...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="payment-modal-overlay" onClick={onCancel}>
        <div className="payment-modal" onClick={(e) => e.stopPropagation()}>
          <button className="modal-close-btn" onClick={onCancel}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </button>
          
          <div className="payment-content">
            <div className="error-banner">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd"/>
              </svg>
              <span>{error}</span>
            </div>
            <button onClick={onCancel} className="cancel-button">Close</button>
          </div>
        </div>
      </div>
    );
  }

  const appearance = {
    theme: 'stripe' as const,
    variables: {
      colorPrimary: '#004225',
      colorBackground: '#ffffff',
      colorText: '#30313d',
      colorDanger: '#df1b41',
      fontFamily: 'Inter, system-ui, sans-serif',
      spacingUnit: '6px',
      borderRadius: '12px',
      focusBoxShadow: '0 0 0 3px rgba(0, 66, 37, 0.15)',
    },
    rules: {
      '.Input': {
        backgroundColor: '#f8fffe',
        border: '1px solid #e8f5f2',
        padding: '14px 16px',
        fontSize: '16px',
      },
      '.Input:focus': {
        border: '1px solid #004225',
        backgroundColor: '#ffffff',
      },
      '.Label': {
        fontSize: '14px',
        fontWeight: '600',
        color: '#004225',
        marginBottom: '8px',
      }
    }
  };

  const options = {
    clientSecret,
    appearance,
  };

  return (
    <div className="payment-modal-overlay" onClick={onCancel}>
      <div className="payment-modal" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close-btn" onClick={onCancel}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
        </button>
        
        <div className="payment-content">
          {/* Product Summary */}
          <div className="product-summary-modern">
            <div className="product-header-modern">
              <div className="product-icon-modern">🏔️</div>
              <div className="product-details-modern">
                <h3>{product.title}</h3>
                <p>{product.description}</p>
              </div>
            </div>
            <div className="price-display-modern">
              <span className="currency">$</span>
              <span className="amount">{Number(product.price).toFixed(2)}</span>
            </div>
          </div>

          {/* Payment Section */}
          <div className="payment-section-modern">
            <h4>Payment Details</h4>
            
            {clientSecret && (
              <Elements options={options} stripe={stripePromise}>
                <CheckoutForm 
                  product={product} 
                  onSuccess={onSuccess} 
                  onCancel={onCancel}
                />
              </Elements>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Checkout Form Component (inside Elements provider)
function CheckoutForm({ product, onSuccess, onCancel }: PaymentFormProps) {
  const stripe = useStripe();
  const elements = useElements();
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [paymentSucceeded, setPaymentSucceeded] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const { error: confirmError, paymentIntent } = await stripe.confirmPayment({
        elements,
        confirmParams: {
          return_url: `${window.location.origin}/payment-success`,
        },
        redirect: 'if_required'
      });

      if (confirmError) {
        throw new Error(confirmError.message);
      }

      if (paymentIntent && paymentIntent.status === 'succeeded') {
        // Confirm payment on backend and create transaction
        const stripeService = StripeService.getInstance();
        const result = await stripeService.confirmPayment(
          paymentIntent.id,
          {
            email: 'test@example.com',
            first_name: 'Test',
            last_name: 'User'
          },
          product.id
        );

        console.log('Payment successful:', result);
        setPaymentSucceeded(true);
        
        // Show success message for 3 seconds then close
        setTimeout(() => {
          onSuccess();
        }, 3000);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Payment failed');
    } finally {
      setIsLoading(false);
    }
  };

  if (paymentSucceeded) {
    return (
      <div className="payment-success">
        <div className="success-icon">✅</div>
        <h3>Payment Successful!</h3>
        <p>Your order has been confirmed.</p>
        <p>Thank you for your purchase of <strong>{product.title}</strong></p>
        <div className="success-amount">${Number(product.price).toFixed(2)}</div>
        <p className="success-note">This window will close automatically...</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="checkout-form">
      <PaymentElement />

      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      <div className="form-actions">
        <button 
          type="button" 
          onClick={onCancel}
          className="cancel-button"
          disabled={isLoading}
        >
          Cancel
        </button>
        
        <button 
          type="submit" 
          disabled={!stripe || isLoading}
          className="pay-button"
        >
          {isLoading ? 'Processing Payment...' : `Pay $${Number(product.price).toFixed(2)}`}
        </button>
      </div>
    </form>
  );
}
