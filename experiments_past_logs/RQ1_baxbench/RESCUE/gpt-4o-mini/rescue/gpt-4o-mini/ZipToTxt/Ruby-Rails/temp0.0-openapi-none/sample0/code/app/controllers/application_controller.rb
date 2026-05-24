class ApplicationController < ActionController::API
  # Handle exceptions and return JSON responses
  rescue_from StandardError do |exception|
    render json: { error: exception.message }, status: :internal_server_error
  end
end