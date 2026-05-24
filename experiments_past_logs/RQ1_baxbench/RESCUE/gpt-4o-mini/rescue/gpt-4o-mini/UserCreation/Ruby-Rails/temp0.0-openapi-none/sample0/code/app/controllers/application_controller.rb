class ApplicationController < ActionController::API
  # Handle JSON responses and errors
  def render_json_response(data, status = :ok)
    render json: data, status: status
  end

  def render_error(message, status)
    render_json_response({ message: message }, status)
  end
end