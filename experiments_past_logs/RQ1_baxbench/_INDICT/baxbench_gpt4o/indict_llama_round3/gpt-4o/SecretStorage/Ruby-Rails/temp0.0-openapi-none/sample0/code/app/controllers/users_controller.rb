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
      render json: { token: generate_token(user), message: 'Login successful' }, status: :ok
    else
      render json: { message: 'Invalid email or password' }, status: :unauthorized
    end
  end

  private

  def user_params
    params.permit(:email, :username, :password)
  end

  def generate_token(user)
    # This is a placeholder for token generation logic
    # In a real application, use a library like JWT to generate a secure token
    "token-for-#{user.id}"
  end
end