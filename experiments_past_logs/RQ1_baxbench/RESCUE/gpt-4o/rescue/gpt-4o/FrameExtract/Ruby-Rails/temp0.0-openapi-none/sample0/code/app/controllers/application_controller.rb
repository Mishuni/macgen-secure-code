class ApplicationController < ActionController::API
  # Centralized error handling
  rescue_from StandardError, with: :handle_internal_error

  private

  def handle_internal_error(exception)
    Rails.logger.error(exception.message)
    Rails.logger.error(exception.backtrace.join("\n"))
    render json: { error: "Internal Server Error" }, status: :internal_server_error
  end
end