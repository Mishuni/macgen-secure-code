Rails.application.configure do
  # Settings specified here will take precedence over those in config/application.rb.

  # Code is reloaded between requests.
  config.cache_classes = false

  # Do not eager load code on boot.
  config.eager_load = false

  # Show full error reports.
  config.consider_all_requests_local = true

  # Enable CORS
  config.middleware.insert_before 0, Rack::Cors do
    allow do
      origins '*'
      resource '*', headers: :any, methods: [:get]
    end
  end
end