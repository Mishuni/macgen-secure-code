Rails.application.configure do
  # Settings specified here will take precedence over those in config/application.rb.
  
  # Code is not reloaded between requests.
  config.cache_classes = true
  
  # Eager load code on boot. This eager loads most of your application in memory, 
  # allowing for faster response times in production.
  config.eager_load = true
  
  # Full error reports are disabled and the public error pages are shown.
  config.consider_all_requests_local = false
  
  # Enable serving of images, stylesheets, and JavaScripts from an asset server.
  # config.asset_host = "http://assets.example.com"
  
  # Enable caching.
  config.action_controller.perform_caching = true
  
  # Don't care if the mailer can't send.
  config.action_mailer.raise_delivery_errors = false
  
  # Print deprecation notices to the Rails logger.
  config.active_support.deprecation = :notify
  
  # Raise an error on page load if there are pending migrations.
  config.active_record.migration_error = :page_load
  
  # Highlight code that triggered database queries in logs.
  config.active_record.verbose_query_logs = true
  
  # Use default logging formatter so that PID and timestamp are not suppressed.
  config.log_formatter = ::Logger::Formatter.new
end