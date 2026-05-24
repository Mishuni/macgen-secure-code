class ApplicationController < ActionController::API
  def current_user
    @current_user ||= User.find_by(id: decoded_token[:user_id]) if decoded_token
  end

  def authenticate_user!
    render json: { message: 'Unauthorized' }, status: :unauthorized unless current_user
  end

  private

  def decoded_token
    token = request.headers['Authorization']&.split(' ')&.last
    return unless token

    begin
      JWT.decode(token, ENV['APP_SECRET'], true, { algorithm: 'HS256' }).first
    rescue JWT::DecodeError
      nil
    end
  end
end