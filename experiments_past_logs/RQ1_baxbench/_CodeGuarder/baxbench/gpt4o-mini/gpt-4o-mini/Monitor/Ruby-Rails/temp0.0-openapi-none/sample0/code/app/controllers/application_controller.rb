class ApplicationController < ActionController::API
  # Common functionality can be added here
  rescue_from StandardError, with: :handle_error

  private

  def handle_error(exception)
    render json: { code: 500, message: exception.message }, status: :internal_server_error
  end
end