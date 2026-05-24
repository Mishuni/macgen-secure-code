class ApplicationController < ActionController::API
  rescue_from StandardError, with: :handle_error

  private

  def handle_error(exception)
    render json: { error: 'An error occurred' }, status: :internal_server_error
  end
end