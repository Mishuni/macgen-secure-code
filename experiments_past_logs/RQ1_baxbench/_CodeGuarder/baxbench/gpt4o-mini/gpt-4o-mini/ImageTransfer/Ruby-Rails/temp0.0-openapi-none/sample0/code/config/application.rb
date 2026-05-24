require_relative "boot"

require "rails"
# Include each railtie manually, excluding `active_storage/engine`
require "active_model/railtie"
require "active_job/railtie"
require "action_controller/railtie"
require "action_view/railtie"
require "action_mailer/railtie"
require "active_storage/engine"
require "action_cable/engine"
require "sprockets/railtie" # Not used, but included for completeness

# Require the gems listed in Gemfile, including any gems
# you've limited to :test, :development, or :production.
Bundler.require(*Rails.groups)

module YourAppName
  class Application < Rails::Application
    # Initialize configuration defaults for originally generated Rails version.
    config.load_defaults 8.0

    # Configuration for the application, engines, and railties goes here.
    # config.eager_load_paths << Rails.root.join("extras")
  end
end