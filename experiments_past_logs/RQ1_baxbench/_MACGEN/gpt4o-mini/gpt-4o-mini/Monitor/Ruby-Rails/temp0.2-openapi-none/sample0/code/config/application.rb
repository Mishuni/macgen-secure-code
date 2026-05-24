require_relative "boot"

require "rails"
# Include each railtie manually, excluding `action_view` and `action_mailer`
require "active_model/railtie"
require "active_job/railtie"
require "action_controller/railtie"
require "active_storage/engine"
require "action_cable/engine"
require "rails/test_unit/railtie"

# Require the gems listed in Gemfile, including any gems
# you've limited to :test, :development, or :production.
Bundler.require(*Rails.groups)

module YourAppName
  class Application < Rails::Application
    # Initialize configuration defaults for originally generated Rails version.
    config.load_defaults 8.0

    # Configuration for the application, engines, and railties goes here.
    config.api_only = true
  end
end