require_relative "boot"
require "rails/all"
require "active_storage/engine"

Bundler.require(*Rails.groups)

module ProductCatalog
  class Application < Rails::Application
    config.load_defaults 8.0
    config.api_only = true
  end
end