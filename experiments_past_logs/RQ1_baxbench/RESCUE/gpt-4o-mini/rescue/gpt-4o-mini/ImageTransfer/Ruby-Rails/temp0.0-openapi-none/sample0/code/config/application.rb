require_relative "boot"

require "rails"
# Include each railtie manually, excluding `active_storage/engine`
require "active_model/railtie"
require "active_controller/railtie"
require "active_job/railtie"
require "active_record/railtie"
require "action_mailer/railtie"
require "action_view/railtie"
require "action_cable/engine"
require "rails/test_unit/railtie"
require "active_storage/engine"

# Require the gems listed in Gemfile, including any gems
# you've limited to :test, :development, or :production.
Bundler.require(*Rails.groups)

module ImageUploadApi
  class Application < Rails::Application
    # Initialize configuration defaults for originally generated Rails version.
    config.load_defaults 8.0

    # Configuration for the application, engines, and railties goes here.
    config.api_only = true
  end
end