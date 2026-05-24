class ApplicationController < ActionController::API
  # Centralized error handling
  rescue_from StandardError, with: :handle_internal_server_error
  rescue_from ActiveRecord::RecordNotFound, with: :handle_not_found

  private

  def handle_internal_server_error(exception)
    render json: { error: "Internal server error: #{exception.message}" }, status: :internal_server_error
  end

  def handle_not_found(exception)
    render json: { error: "Resource not found: #{exception.message}" }, status: :not_found
  end
end