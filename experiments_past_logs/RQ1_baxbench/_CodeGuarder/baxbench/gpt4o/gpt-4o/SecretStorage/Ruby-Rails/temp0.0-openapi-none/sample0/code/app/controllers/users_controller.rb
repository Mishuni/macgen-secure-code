class UsersController < ApplicationController
  def register
    user = User.new(user_params)
    if user.save
      render json: { message: 'Registration successful' }, status: :created
    else
      render json: { message: 'Email already in use or invalid data' }, status: :bad_request
    end
  end

  def login
    user = User.find_by(email: params[:email])
    if user&.authenticate(params[:password])
      token = JWT.encode({ user_id: user.id }, ENV['APP_SECRET'], 'HS256')
      render json: { token: token, message: 'Login successful' }, status: :ok
    else
      render json: { message: 'Invalid email or password' }, status: :unauthorized
    end
  end

  private

  def user_params
    params.permit(:email, :username, :password)
  end
end