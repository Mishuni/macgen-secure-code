class ApplicationController < ActionController::API
  rescue_from StandardError, with: :handle_internal_server_error
  rescue_from ActionController::ParameterMissing, with: :handle_bad_request

  private

  def handle_internal_server_error(exception)
    Rails.logger.error(exception.message)
    Rails.logger.error(exception.backtrace.join("\n"))
    render json: { error: 'Internal server error' }, status: :internal_server_error
  end

  def handle_bad_request(exception)
    render json: { error: exception.message }, status: :bad_request
  end
end