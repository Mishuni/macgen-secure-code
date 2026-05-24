class ApplicationController < ActionController::API
  rescue_from StandardError, with: :handle_internal_server_error

  private

  def handle_internal_server_error(exception)
    render json: { error: "An error occurred. Please try again later." }, status: :internal_server_error
  end
end