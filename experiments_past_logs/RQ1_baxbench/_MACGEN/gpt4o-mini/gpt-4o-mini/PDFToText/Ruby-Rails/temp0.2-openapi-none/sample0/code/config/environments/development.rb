Rails.application.configure do
  config.consider_all_requests_local = false
  config.cache_classes = false
  config.eager_load = false
  config.log_level = :debug
  config.action_controller.perform_caching = false
end