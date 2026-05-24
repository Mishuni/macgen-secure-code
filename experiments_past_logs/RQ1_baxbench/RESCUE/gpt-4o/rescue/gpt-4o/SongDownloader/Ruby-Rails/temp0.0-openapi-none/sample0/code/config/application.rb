require_relative "boot"

require "rails"
require "active_model/railtie"
require "active_job/railtie"
require "active_record/railtie"
require "action_controller/railtie"
require "action_mailer/railtie"
require "rails/test_unit/railtie"
require "active_storage/engine"

# Require the gems listed in Gemfile, including any gems
# you've limited to :test, :development, or :production.
Bundler.require(*Rails.groups)

module SongDownloader
  class Application < Rails::Application
    config.load_defaults 8.0

    # Only loads a smaller set of middleware suitable for API only apps.
    config.api_only = true

    # Add middleware for CORS
    config.middleware.insert_before 0, Rack::Cors do
      allow do
        origins '*'
        resource '*',
                 headers: :any,
                 methods: %i[get post options],
                 expose: %w[Access-Control-Allow-Origin Access-Control-Allow-Headers]
      end
    end
  end
end