class ApplicationController < ActionController::API
  def render_error(message, code = 400)
    render json: { code: code, message: message }, status: code
  end
end