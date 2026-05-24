class ApplicationController < ActionController::API
  rescue_from StandardError, with: :handle_error

  private

  def handle_error(exception)
    render json: { error: exception.message }, status: :bad_request
  end
end