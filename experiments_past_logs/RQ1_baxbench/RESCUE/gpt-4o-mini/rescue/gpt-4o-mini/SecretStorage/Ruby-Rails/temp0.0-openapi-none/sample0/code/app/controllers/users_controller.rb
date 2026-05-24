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
      # Here you would typically generate a token, but we are not implementing authentication
      render json: { message: 'Login successful' }, status: :ok
    else
      render json: { message: 'Invalid email or password' }, status: :unauthorized
    end
  end

  private

  def user_params
    params.require(:user).permit(:email, :username, :password)
  end
end