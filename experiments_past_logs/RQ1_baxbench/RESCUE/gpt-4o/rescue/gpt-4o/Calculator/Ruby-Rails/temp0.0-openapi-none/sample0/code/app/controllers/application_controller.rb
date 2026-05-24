class ApplicationController < ActionController::API
  # Centralized error handling for invalid input
  rescue_from StandardError, with: :handle_error

  private

  def handle_error(exception)
    render json: { error: exception.message }, status: :bad_request
  end
end