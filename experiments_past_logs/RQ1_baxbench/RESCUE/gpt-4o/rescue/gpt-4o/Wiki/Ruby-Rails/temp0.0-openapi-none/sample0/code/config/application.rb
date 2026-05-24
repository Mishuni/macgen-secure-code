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

module WikiApi
  class Application < Rails::Application
    config.load_defaults 8.0

    # Use SQLite database
    config.active_record.sqlite3.represent_boolean_as_integer = true

    # Middleware for CORS
    config.middleware.insert_before 0, Rack::Cors do
      allow do
        origins '*'
        resource '*', headers: :any, methods: %i[get post put options]
      end
    end
  end
end