require_relative "boot"

require "rails/all"

# Require the gems listed in Gemfile, including any gems
# you've limited to :test, :development, or :production.
Bundler.require(*Rails.groups)

module ShopifyApi
  class Application < Rails::Application
    # Initialize configuration defaults for originally generated Rails version.
    config.load_defaults 8.0

    # Please, add to the `ignore` list any other `lib` subdirectories that do
    # not contain `.rb` files, or that should not be reloaded or eager loaded.
    # Common ones are `templates`, `generators`, or `middleware`, for example.
    config.autoload_lib(ignore: %w[assets tasks])

    # Configuration for the application, engines, and railties goes here.
    #
    # These settings can be overridden in specific environments using the files
    # in config/environments, which are processed later.
    #
    # config.time_zone = "Central Time (US & Canada)"
    # config.eager_load_paths << Rails.root.join("extras")

    # Only loads a smaller set of middleware suitable for API only apps.
    # Middleware like session, flash, cookies can be added back manually.
    # Skip views, helpers and assets when generating a new resource.
    config.api_only = true

    # Initialize Shopify API Context for private app
    ShopifyAPI::Context.setup(
      api_key: ENV['SHOPIFY_API_KEY'] || 'dummy_key',
      api_secret_key: ENV['SHOPIFY_API_SECRET'] || 'dummy_secret',
      host: ENV['SHOPIFY_HOST'] || 'https://localhost:3000',
      scope: "read_products,read_orders,read_customers",
      is_embedded: false,
      api_version: "2024-01",
      is_private: true  # Set to true for private app with access token
    )
  end
end
