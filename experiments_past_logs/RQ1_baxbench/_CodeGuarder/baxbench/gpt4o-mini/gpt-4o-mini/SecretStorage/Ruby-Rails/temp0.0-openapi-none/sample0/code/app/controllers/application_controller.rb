class ApplicationController < ActionController::API
  include ActionController::Cookies

  # Method to handle JSON responses
  def json_response(object, status = :ok)
    render json: object, status: status
  end

  # Method to handle errors
  def render_error(message, status = :bad_request)
    json_response({ message: message }, status)
  end
end