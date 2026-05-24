Rails.application.configure do
  # Settings specified here will take precedence over those in config/application.rb.

  # Code is reloaded between requests.
  config.cache_classes = false

  # Do not eager load code on boot.
  config.eager_load = false

  # Show full error reports.
  config.consider_all_requests_local = true

  # Enable/disable caching. By default caching is disabled.
  # config.action_controller.perform_caching = false

  # Store uploaded files on the local file system.
  # config.active_storage.service = :local

  # Raise exceptions instead of rendering exception templates.
  config.action_dispatch.show_exceptions = false

  # Disable request forgery protection in API mode.
  config.action_controller.allow_forgery_protection = false

  # Print deprecation notices to the Rails logger.
  config.active_support.deprecation = :log

  # Raise an error on page load if there are pending migrations.
  config.active_record.migration_error = :page_load

  # Highlight code that triggered database queries in logs.
  config.active_record.verbose_query_logs = true

  # Raises error for missing translations.
  # config.i18n.raise_on_missing_translations = true

  # Annotate rendered view with file names.
  # config.action_view.annotate_rendered_view_with_filenames = true

  # Disable serving static files from the `/public` folder by default since
  # Apache or NGINX already handles this.
  config.public_file_server.enabled = true

  # Compress JavaScripts and CSS.
  # config.assets.js_compressor = :uglifier

  # Do not fallback to assets pipeline if a precompiled asset is missed.
  # config.assets.compile = false

  # Generate digests for assets URLs.
  # config.assets.digest = true

  # Force all access to the app over SSL, use Strict-Transport-Security, and use secure cookies.
  # config.force_ssl = true

  # Use the lowest log level to ensure availability of diagnostic information
  # in production.
  config.log_level = :debug

  # Use a different logger for distributed setups.
  # config.logger = ActiveSupport::TaggedLogging.new(Syslog::Logger.new 'app-name')

  # Use a different cache store in production.
  # config.cache_store = :memory_store

  # Enable serving of images, stylesheets, and JavaScripts from an asset server.
  # config.action_controller.asset_host = 'http://assets.example.com'

  # Prepend all log lines with the following tags.
  # config.log_tags = [ :subdomain, :uuid ]

  # Use a different cache store in production.
  # config.cache_store = :memory_store

  # Use default locale as :en and load all translations from
  # config/locales/*.rb,yml.
  # config.i18n.default_locale = :de

  # Set the time zone default.
  # config.time_zone = 'Central Time (US & Canada)'

  # Configure the default encoding used in templates for Ruby 1.9.
  # config.encoding = "utf-8"

  # Enable serving of static files from the `/public` folder by default since
  # Apache or NGINX already handles this.
  config.public_file_server.enabled = true
end