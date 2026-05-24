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

module LoginApi
  class Application < Rails::Application
    config.load_defaults 8.0

    # API-only configuration
    config.api_only = true
  end
end