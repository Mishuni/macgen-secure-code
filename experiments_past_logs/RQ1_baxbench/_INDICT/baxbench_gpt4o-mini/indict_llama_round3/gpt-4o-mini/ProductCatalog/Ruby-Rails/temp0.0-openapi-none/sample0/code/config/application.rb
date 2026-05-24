require_relative "boot"

require "rails"
# Include each railtie manually, excluding `active_record/railtie` which is not needed
require "active_model/railtie"
require "active_job/railtie"
require "action_controller/railtie"
require "action_view/railtie"
require "action_mailer/railtie"
require "active_storage/engine"

# Require the gems listed in Gemfile, including any gems
# you've limited to :test, :development, or :production.
Bundler.require(*Rails.groups)

module ProductCatalog
  class Application < Rails::Application
    config.api_only = true
  end
end