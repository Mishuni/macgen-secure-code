class AuthenticationController < ApplicationController
  def login
    user = User.find_by(email: params[:email])

    if user&.authenticate(params[:password])
      render json: { token: "jwt-token-abc123", message: "Login successful" }, status: :ok
    else
      render json: { message: "Invalid email or password" }, status: :unauthorized
    end
  end

  def register
    user = User.new(user_params)

    if user.save
      render json: { message: "Registration successful" }, status: :created
    else
      render json: { message: "Email already in use or invalid data" }, status: :bad_request
    end
  end

  private

  def user_params
    params.permit(:email, :password, :name)
  end
end