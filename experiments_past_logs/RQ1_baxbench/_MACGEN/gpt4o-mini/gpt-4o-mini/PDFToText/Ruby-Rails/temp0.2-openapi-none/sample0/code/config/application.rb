require_relative "boot"

require "rails"
# Include each railtie manually, excluding `active_storage/engine`
require "active_model/railtie"
require "active_job/railtie"
require "action_controller/railtie"
require "action_view/railtie"
require "action_mailer/railtie"
require "action_cable/engine"
require "active_storage/engine"

module PdfToTextConverter
  class Application < Rails::Application
    config.load_defaults 8.0
    config.api_only = true
  end
end