Rails.application.configure do
  config.cache_classes = false
  config.eager_load = false
  config.consider_all_requests_local = true
  config.assets.debug = true
  config.assets.digest = true
  config.active_support.deprecation = :log
  config.file_watcher = ActiveSupport::FileUpdateChecker
end