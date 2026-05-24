class AuthenticationController < ApplicationController
  def login
    user = User.find_by(email: params[:email])
    if user&.authenticate(params[:password])
      token = generate_jwt(user) # Generate a JWT token for the user
      render json: { token: token, message: "Login successful" }, status: :ok
    else
      render json: { message: "Invalid email or password" }, status: :unauthorized
    end
  end

  def register
    user = User.new(user_params)
    if user.save
      render json: { message: "Registration successful" }, status: :created
    else
      render json: { message: user.errors.full_messages.join(", ") }, status: :bad_request
    end
  end

  private

  def user_params
    params.require(:user).permit(:email, :password, :name)
  end

  def generate_jwt(user)
    # Implement JWT generation logic using the APP_SECRET environment variable
    payload = { user_id: user.id, exp: 24.hours.from_now.to_i }
    JWT.encode(payload, ENV['APP_SECRET'])
  end
end