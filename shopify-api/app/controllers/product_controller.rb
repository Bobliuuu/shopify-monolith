class ProductController < ApplicationController
  def index
    # Initialize Shopify API client
    unless setup_shopify_client
      return # Early return if setup failed
    end
    
    # Get limit parameter (optional)
    limit = params[:limit]&.to_i
    
    # Get products from Shopify (no limit if not specified)
    products = get_shopify_products(limit)
    
    # Early return if products fetch failed
    return if products.nil?
    
    # Return JSON data directly
    render json: {
      message: "Products fetched successfully",
      limit: limit,
      products_count: products.length,
      products: products
    }
  end

  private

  def setup_shopify_client
    # Load environment variables
    domain = ENV['SHOPIFY_DOMAIN'] || 'shop-monolith.myshopify.com'
    access_token = ENV['SHOPIFY_ACCESS_TOKEN'] || '***REMOVED***'
    
    # Initialize Shopify API client with correct parameters
    @client = ShopifyAPI::Clients::Rest::Admin.new(
      session: ShopifyAPI::Auth::Session.new(
        shop: domain,
        access_token: access_token
      )
    )
    true
  rescue => e
    Rails.logger.error "Failed to setup Shopify client: #{e.message}"
    render json: { error: "Failed to setup Shopify client: #{e.message}" }, status: 500
    false
  end

  def get_shopify_products(limit = nil)
    begin
      query_params = {}
      query_params[:limit] = limit if limit
      
      response = @client.get(
        path: 'products',
        query: query_params
      )
      
      # The response is already a Hash, no need to parse JSON
      data = response.body
      products = data['products'] || []
      
      Rails.logger.info "Fetched #{products.length} products from Shopify"
      Rails.logger.info "Products: #{products.map { |p| p['title'] }.join(', ')}"
      
      products
    rescue => e
      Rails.logger.error "Failed to fetch products from Shopify: #{e.message}"
      render json: { error: "Failed to fetch products from Shopify: #{e.message}" }, status: 500
      return nil
    end
  end


end