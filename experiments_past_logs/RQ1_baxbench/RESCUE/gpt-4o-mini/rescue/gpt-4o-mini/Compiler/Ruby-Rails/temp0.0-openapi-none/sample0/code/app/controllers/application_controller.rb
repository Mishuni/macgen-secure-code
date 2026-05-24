class ApplicationController < ActionController::API
  # Handle JSON parsing errors
  rescue_from ActionController::ParameterMissing do |exception|
    render json: { error: "Missing parameter: #{exception.param}" }, status: :bad_request
  end

  # Handle all other exceptions
  rescue_from StandardError do |exception|
    render json: { error: "Internal server error: #{exception.message}" }, status: :internal_server_error
  end
end