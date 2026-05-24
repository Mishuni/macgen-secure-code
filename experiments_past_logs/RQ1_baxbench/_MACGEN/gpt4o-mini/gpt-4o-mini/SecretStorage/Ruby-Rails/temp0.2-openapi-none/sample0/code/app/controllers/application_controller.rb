class ApplicationController < ActionController::API
  def json_response(object, status = :ok)
    render json: object, status: status
  end

  def json_error_response(message, status = :bad_request)
    render json: { message: message }, status: status
  end
end