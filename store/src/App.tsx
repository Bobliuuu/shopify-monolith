import "./index.css";
import { useState, useEffect } from 'react';
import { PaymentForm } from './services/StripeService';

interface Product {
  id: number;
  title: string;
  description: string;
  price: number;
  inventory_quantity: number;
  status: string;
}

interface Customer {
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
}

export function App() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentView, setCurrentView] = useState<'store' | 'admin'>('store');
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  // Fetch products
  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:3000/api/products');
      if (!response.ok) {
        throw new Error('Failed to fetch products');
      }
      const data = await response.json();
      setProducts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handlePurchase = async (product: Product) => {
    setSelectedProduct(product);
  };

  const handlePaymentSuccess = () => {
    setSelectedProduct(null);
    fetchProducts(); // Refresh products to update inventory
  };

  const handlePaymentCancel = () => {
    setSelectedProduct(null);
  };

  if (loading) {
    return <div className="app"><div className="loading">Loading...</div></div>;
  }

  if (error) {
    return <div className="app"><div className="error">Error: {error}</div></div>;
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🏂 Snowboard Store</h1>
        <nav>
          <button 
            className={currentView === 'store' ? 'active' : ''}
            onClick={() => setCurrentView('store')}
          >
            Store
          </button>
          <button 
            className={currentView === 'admin' ? 'active' : ''}
            onClick={() => setCurrentView('admin')}
          >
            Admin
          </button>
        </nav>
      </header>

      {selectedProduct ? (
        <PaymentForm
          product={selectedProduct}
          onSuccess={handlePaymentSuccess}
          onCancel={handlePaymentCancel}
        />
      ) : currentView === 'store' ? (
        <StoreView products={products} onPurchase={handlePurchase} />
      ) : (
        <AdminView onProductAdded={fetchProducts} />
      )}
    </div>
  );
}

// Store View Component
function StoreView({ products, onPurchase }: { 
  products: Product[]; 
  onPurchase: (product: Product) => void; 
}) {
  return (
    <div className="store-view">
      <div className="hero">
        <h2>Premium Snowboards for Every Adventure</h2>
        <p>Discover our collection of high-quality snowboards</p>
      </div>
      
      <div className="products-grid">
        {products.length === 0 ? (
          <p>No products available</p>
        ) : (
          products.map(product => (
            <div key={product.id} className="product-card">
              <div className="product-image">
                <div className="placeholder-image">🏂</div>
              </div>
              <div className="product-info">
                <h3>{product.title}</h3>
                <p className="description">{product.description}</p>
                <div className="price">${product.price}</div>
                <div className="inventory">
                  {product.inventory_quantity > 0 ? 
                    `${product.inventory_quantity} in stock` : 
                    'Out of stock'
                  }
                </div>
                <button 
                  className="buy-button"
                  onClick={() => onPurchase(product)}
                  disabled={product.inventory_quantity === 0}
                >
                  {product.inventory_quantity > 0 ? 'Buy Now' : 'Sold Out'}
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

// Admin View Component
function AdminView({ onProductAdded }: { onProductAdded: () => void }) {
  const [showAddProduct, setShowAddProduct] = useState(false);

  return (
    <div className="admin-view">
      <h2>Admin Dashboard</h2>
      
      <div className="admin-actions">
        <button 
          className="action-button"
          onClick={() => setShowAddProduct(!showAddProduct)}
        >
          {showAddProduct ? 'Cancel' : 'Add Product'}
        </button>
      </div>

      {showAddProduct && (
        <AddProductForm 
          onSuccess={() => {
            setShowAddProduct(false);
            onProductAdded();
          }}
        />
      )}
    </div>
  );
}

// Add Product Form Component
function AddProductForm({ onSuccess }: { onSuccess: () => void }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    price: '',
    inventory_quantity: '',
    sku: '',
    vendor: 'Snowboard Co',
    product_type: 'Snowboard'
  });

  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const response = await fetch('http://localhost:3000/api/products', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          price: parseFloat(formData.price),
          inventory_quantity: parseInt(formData.inventory_quantity),
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to add product');
      }

      alert('Product added successfully!');
      onSuccess();
    } catch (err) {
      alert('Failed to add product. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  return (
    <form className="add-product-form" onSubmit={handleSubmit}>
      <h3>Add New Product</h3>
      
      <div className="form-group">
        <label htmlFor="title">Title *</label>
        <input
          type="text"
          id="title"
          name="title"
          value={formData.title}
          onChange={handleChange}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="description">Description</label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          rows={3}
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="price">Price *</label>
          <input
            type="number"
            id="price"
            name="price"
            value={formData.price}
            onChange={handleChange}
            step="0.01"
            min="0"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="inventory_quantity">Inventory *</label>
          <input
            type="number"
            id="inventory_quantity"
            name="inventory_quantity"
            value={formData.inventory_quantity}
            onChange={handleChange}
            min="0"
            required
          />
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="sku">SKU</label>
        <input
          type="text"
          id="sku"
          name="sku"
          value={formData.sku}
          onChange={handleChange}
        />
      </div>

      <button type="submit" disabled={submitting}>
        {submitting ? 'Adding...' : 'Add Product'}
      </button>
    </form>
  );
}

export default App;
