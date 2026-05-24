require_relative "boot"

require "rails"
# Include each railtie manually, excluding `action_cable/engine`
require "active_model/railtie"
require "active_job/railtie"
require "active_record/railtie"
require "action_controller/railtie"
require "action_view/railtie"
require "action_mailer/railtie"
require "active_storage/engine"
require "rails/test_unit/railtie"

Bundler.require(*Rails.groups)

module ServiceMonitoringAPI
  class Application < Rails::Application
    config.load_defaults 8.0
    config.api_only = true
  end
end