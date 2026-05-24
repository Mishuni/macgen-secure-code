class SessionsController < ApplicationController
  def create
    user = User.find_by(email: params[:email])
    if user&.authenticate(params[:password])
      json_response({ token: 'jwt-token-abc123', message: 'Login successful' })
    else
      json_response({ message: 'Invalid email or password' }, :unauthorized)
    end
  end
end