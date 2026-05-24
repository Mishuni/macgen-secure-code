require_relative "boot"

require "rails"
require "active_model/railtie"
require "active_job/railtie"
require "active_record/railtie"
require "active_storage/engine"
require "action_controller/railtie"
require "action_mailer/railtie"
require "action_view/railtie"
require "action_cable/engine"

Bundler.require(*Rails.groups)

module GifCreatorApi
  class Application < Rails::Application
    config.load_defaults 8.0

    # API-only configuration
    config.api_only = true

    # Use SQLite as the database
    config.active_record.sqlite3.represent_boolean_as_integer = true
  end
end