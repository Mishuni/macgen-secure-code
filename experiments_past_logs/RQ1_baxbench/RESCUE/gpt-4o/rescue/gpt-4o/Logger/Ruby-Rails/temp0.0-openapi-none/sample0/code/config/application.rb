require_relative "boot"

require "rails"
# Include each railtie manually, excluding sprockets
require "active_model/railtie"
require "active_job/railtie"
require "active_record/railtie"
require "action_controller/railtie"
require "action_mailer/railtie"
require "action_view/railtie"
require "active_storage/engine"

# Require the gems listed in Gemfile, including any gems
# you've limited to :test, :development, or :production.
Bundler.require(*Rails.groups)

module LoggingApi
  class Application < Rails::Application
    config.load_defaults 8.0

    # Only loads a smaller set of middleware suitable for API only apps.
    config.api_only = true

    # Set the default encoding to UTF-8
    config.encoding = "utf-8"

    # Use SQLite as the database
    config.active_record.sqlite3.represent_boolean_as_integer = true
  end
end