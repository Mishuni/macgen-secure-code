require_relative "boot"

require "rails"
# Include each railtie manually, excluding `action cable` and `active storage`
require "active_model/railtie"
require "active_record/railtie"
require "action_controller/railtie"
require "action_view/railtie"
require "action_mailer/railtie"
require "active_job/railtie"
require "rack/cors"

module RecipeSharingApp
  class Application < Rails::Application
    config.load_defaults 8.0
    config.api_only = true
    config.middleware.insert_before 0, Rack::Cors do
      allow do
        origins '*'
        resource '*', headers: :any, methods: [:get, :post]
      end
    end
  end
end