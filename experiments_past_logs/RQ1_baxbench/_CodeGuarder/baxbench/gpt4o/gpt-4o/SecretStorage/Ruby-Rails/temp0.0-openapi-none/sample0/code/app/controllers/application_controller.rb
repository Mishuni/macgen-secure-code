class ApplicationController < ActionController::API
  before_action :authenticate_request, except: [:register, :login]

  private

  def authenticate_request
    token = request.headers['Authorization']&.split(' ')&.last
    if token
      begin
        decoded_token = JWT.decode(token, ENV['APP_SECRET'], true, { algorithm: 'HS256' })
        @current_user = User.find(decoded_token[0]['user_id'])
      rescue JWT::DecodeError
        render json: { message: 'Invalid authentication token' }, status: :unauthorized
      end
    else
      render json: { message: 'Missing authentication token' }, status: :unauthorized
    end
  end
end