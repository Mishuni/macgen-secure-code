require_relative "boot"

require "rails"
require "active_model/railtie"
require "active_job/railtie"
require "active_record/railtie"
require "action_controller/railtie"
require "action_mailer/railtie"
require "rails/test_unit/railtie"
require "active_storage/engine"

Bundler.require(*Rails.groups)

module FrameExtract
  class Application < Rails::Application
    config.load_defaults 8.0

    # Use SQLite as the database
    config.active_record.sqlite3.represent_boolean_as_integer = true

    # Disable asset pipeline
    config.assets.enabled = false

    # Set default middleware for API-only apps
    config.api_only = true
  end
end