class ApplicationController < ActionController::API
  # Handle exceptions and return a JSON response
  rescue_from StandardError do |exception|
    render json: { error: exception.message }, status: :internal_server_error
  end
end