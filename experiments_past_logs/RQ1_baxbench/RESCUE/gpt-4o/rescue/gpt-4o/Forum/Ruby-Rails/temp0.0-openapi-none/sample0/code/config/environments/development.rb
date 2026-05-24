require "active_support/core_ext/integer/time"

Rails.application.configure do
  # Settings specified here will take precedence over those in config/application.rb.

  # Code is reloaded between requests in development
  config.cache_classes = false

  # Eager load code on boot
  config.eager_load = false

  # Show full error reports
  config.consider_all_requests_local = true

  # Store files locally
  config.active_storage.service = :local

  # Disable asset pipeline
  config.assets.enabled = false

  # Use an evented file watcher
  config.file_watcher = ActiveSupport::EventedFileUpdateChecker
end