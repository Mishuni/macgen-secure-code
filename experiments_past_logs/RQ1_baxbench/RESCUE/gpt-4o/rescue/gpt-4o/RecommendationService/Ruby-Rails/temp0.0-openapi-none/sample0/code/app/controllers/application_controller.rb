class ApplicationController < ActionController::API
  rescue_from StandardError, with: :handle_internal_error

  private

  def handle_internal_error(exception)
    render json: { error: exception.message }, status: :internal_server_error
  end
end