class AuthenticationController < ApplicationController
  # POST /login
  def login
    user = User.find_by(email: params[:email])
    if user&.password == params[:password]
      render json: { token: "jwt-token-placeholder", message: "Login successful" }, status: :ok
    else
      render json: { message: "Invalid email or password" }, status: :unauthorized
    end
  end

  # POST /register
  def register
    user = User.create!(user_params)
    render json: { message: "Registration successful" }, status: :created
  end

  private

  def user_params
    params.require(:user).permit(:email, :password, :name)
  end
end