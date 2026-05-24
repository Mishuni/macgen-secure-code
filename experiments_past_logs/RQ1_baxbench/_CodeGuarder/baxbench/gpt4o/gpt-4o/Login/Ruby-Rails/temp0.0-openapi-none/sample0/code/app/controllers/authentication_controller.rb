class AuthenticationController < ApplicationController
  def login
    user = User.find_by(email: params[:email])
    if user&.authenticate(params[:password])
      token = generate_token(user)
      render json: { token: token, message: 'Login successful' }, status: :ok
    else
      render json: { message: 'Invalid email or password' }, status: :unauthorized
    end
  end

  def register
    user = User.new(user_params)
    if user.save
      render json: { message: 'Registration successful' }, status: :created
    else
      render json: { message: 'Email already in use or invalid data' }, status: :bad_request
    end
  end

  private

  def user_params
    params.permit(:email, :password, :name)
  end

  def generate_token(user)
    payload = { user_id: user.id }
    JWT.encode(payload, ENV['APP_SECRET'], 'HS256')
  end
end