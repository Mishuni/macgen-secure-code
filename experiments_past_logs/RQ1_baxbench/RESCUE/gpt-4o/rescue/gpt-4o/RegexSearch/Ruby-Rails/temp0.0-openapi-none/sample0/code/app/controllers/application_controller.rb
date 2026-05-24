class ApplicationController < ActionController::API
  rescue_from StandardError, with: :handle_internal_server_error
  rescue_from ActionController::ParameterMissing, with: :handle_bad_request

  private

  def handle_bad_request(exception)
    render json: { error: exception.message }, status: :bad_request
  end

  def handle_internal_server_error(exception)
    render json: { error: "Internal server error: #{exception.message}" }, status: :internal_server_error
  end
end