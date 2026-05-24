require "active_support/core_ext/integer/time"

Rails.application.configure do
  # Settings specified here will take precedence over those in config/application.rb.

  # Code is reloaded between requests in development
  config.cache_classes = false

  # Eager load code on boot
  config.eager_load = false

  # Show full error reports
  config.consider_all_requests_local = true

  # Disable asset pipeline
  config.assets.enabled = false

  # Use default logging formatter
  config.log_formatter = ::Logger::Formatter.new
end