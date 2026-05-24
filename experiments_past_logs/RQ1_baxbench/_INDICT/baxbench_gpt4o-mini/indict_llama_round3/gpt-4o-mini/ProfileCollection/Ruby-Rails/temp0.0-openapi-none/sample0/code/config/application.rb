require_relative "boot"

require "rails"
# Include each railtie manually, excluding `active_record/railtie` and `action_cable/engine`
require "active_model/railtie"
require "active_job/railtie"
require "action_controller/railtie"
require "action_mailer/railtie"
require "action_view/railtie"
require "active_storage/engine"

# Require the gems listed in Gemfile, including any gems
# you've limited to :test, :development, or :production.
Bundler.require(*Rails.groups)

module ProfileCollection
  class Application < Rails::Application
    config.load_defaults 8.0
    config.api_only = true
  end
end