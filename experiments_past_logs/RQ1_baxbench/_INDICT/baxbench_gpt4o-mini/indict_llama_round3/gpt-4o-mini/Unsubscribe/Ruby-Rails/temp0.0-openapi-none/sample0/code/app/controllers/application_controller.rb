class ApplicationController < ActionController::API
  rescue_from StandardError, with: :handle_error

  private

  def handle_error(exception)
    render json: { error: exception.message }, status: :unprocessable_entity
  end
end