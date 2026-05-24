class ApplicationController < ActionController::API
  include ActionController::RequestForgeryProtection
  protect_from_forgery with: :exception

  rescue_from StandardError, with: :handle_internal_server_error
  rescue_from ActionController::ParameterMissing, with: :handle_bad_request

  private

  def handle_bad_request(exception)
    render json: { error: exception.message }, status: :bad_request
  end

  def handle_internal_server_error(exception)
    render json: { error: 'Internal Server Error' }, status: :internal_server_error
  end
end