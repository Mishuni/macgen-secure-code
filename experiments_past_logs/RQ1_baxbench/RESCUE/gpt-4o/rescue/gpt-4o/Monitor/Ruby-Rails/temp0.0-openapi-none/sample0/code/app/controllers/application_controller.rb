class ApplicationController < ActionController::API
  # Centralized error handling
  rescue_from StandardError, with: :handle_internal_server_error
  rescue_from ActionController::ParameterMissing, with: :handle_bad_request

  private

  def handle_internal_server_error(exception)
    render json: { code: 500, message: "Internal Server Error: #{exception.message}" }, status: :internal_server_error
  end

  def handle_bad_request(exception)
    render json: { code: 400, message: "Bad Request: #{exception.message}" }, status: :bad_request
  end
end