class UsersController < ApplicationController
  def register
    user = User.create!(user_params)
    render json: { message: "Registration successful" }, status: :created
  rescue ActiveRecord::RecordInvalid => e
    render json: { message: e.message }, status: :bad_request
  end

  def login
    user = User.find_by(email: params[:email])
    if user&.authenticate(params[:password])
      render json: { token: "jwt-token-abc123", message: "Login successful" }, status: :ok
    else
      render json: { message: "Invalid email or password" }, status: :unauthorized
    end
  end

  private

  def user_params
    params.require(:user).permit(:email, :username, :password)
  end
end