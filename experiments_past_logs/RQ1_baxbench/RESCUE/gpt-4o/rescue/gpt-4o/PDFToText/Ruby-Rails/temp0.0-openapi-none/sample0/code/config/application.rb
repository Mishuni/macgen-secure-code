require_relative "boot"

require "rails"
require "active_model/railtie"
require "active_job/railtie"
require "active_record/railtie"
require "active_storage/engine"
require "action_controller/railtie"
require "action_mailer/railtie"
require "action_view/railtie"
require "action_cable/engine"

# Require the gems listed in Gemfile, including any gems
# you've limited to :test, :development, or :production.
Bundler.require(*Rails.groups)

module PdfToTextConverter
  class Application < Rails::Application
    config.load_defaults 8.0

    # Only loads a smaller set of middleware suitable for API only apps.
    config.api_only = true

    # Set the default encoding for JSON responses
    config.action_dispatch.default_headers = {
      'Content-Type' => 'application/json'
    }
  end
end