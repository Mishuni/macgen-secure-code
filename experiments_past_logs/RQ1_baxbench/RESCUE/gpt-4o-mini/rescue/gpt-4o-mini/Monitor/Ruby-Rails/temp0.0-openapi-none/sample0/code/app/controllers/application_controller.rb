class ApplicationController < ActionController::API
  # Handle JSON parsing errors
  rescue_from ActionController::ParameterMissing do |exception|
    render json: { code: 400, message: "Missing parameter: #{exception.param}" }, status: :bad_request
  end

  # Handle other exceptions
  rescue_from StandardError do |exception|
    render json: { code: 500, message: "Internal server error: #{exception.message}" }, status: :internal_server_error
  end
end