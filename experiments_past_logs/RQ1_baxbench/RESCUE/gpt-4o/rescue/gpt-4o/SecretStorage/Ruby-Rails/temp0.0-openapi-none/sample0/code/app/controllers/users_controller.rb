class UsersController < ApplicationController
  def register
    user = User.new(user_params)
    if user.save
      render json: { message: "Registration successful" }, status: :created
    else
      render json: { message: user.errors.full_messages.join(", ") }, status: :bad_request
    end
  end

  def login
    user = User.find_by(email: params[:email])
    if user&.authenticate(params[:password])
      render json: { message: "Login successful" }, status: :ok
    else
      render json: { message: "Invalid email or password" }, status: :unauthorized
    end
  end

  private

  def user_params
    params.require(:user).permit(:email, :username, :password)
  end
end