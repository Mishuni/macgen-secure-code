class SessionsController < ApplicationController
  def create
    return json_response({ message: 'Email and password are required' }, :bad_request) unless params[:email].present? && params[:password].present?

    user = User.find_by(email: params[:email])
    if user&.authenticate(params[:password])
      json_response({ token: 'jwt-token-abc123', message: 'Login successful' })
    else
      json_response({ message: 'Invalid email or password' }, :unauthorized)
    end
  end
end