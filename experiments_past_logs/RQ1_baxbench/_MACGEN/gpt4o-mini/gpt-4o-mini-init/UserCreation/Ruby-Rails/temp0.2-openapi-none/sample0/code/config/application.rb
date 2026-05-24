require_relative "boot"

require "rails"
# Include each railtie manually, excluding `action cable` and `action mailer`
require "active_model/railtie"
require "active_record/railtie"
require "active_storage/engine"
require "action_controller/railtie"
require "action_view/railtie"
require "action_mailer/railtie"
require "active_job/railtie"
require "rack/cors"

# Require the gems listed in Gemfile, including any gems
# you've limited to :test, :development, or :production.
Bundler.require(*Rails.groups)

module InviteApi
  class Application < Rails::Application
    config.load_defaults 8.0
    config.middleware.insert_before 0, Rack::Cors do
      allow do
        origins '*'
        resource '*', headers: :any, methods: [:post]
      end
    end
  end
end