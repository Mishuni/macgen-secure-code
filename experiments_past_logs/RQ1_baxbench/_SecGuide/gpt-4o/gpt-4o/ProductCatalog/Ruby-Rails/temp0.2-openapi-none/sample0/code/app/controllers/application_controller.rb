class ApplicationController < ActionController::API
  # Enable CSRF protection if the application serves HTML
  protect_from_forgery with: :exception if Rails.env.html?
end