class ApplicationController < ActionController::API
  rescue_from StandardError, with: :handle_error

  private

  def handle_error(exception)
    render json: { error: exception.message }, status: :internal_server_error
  end
end