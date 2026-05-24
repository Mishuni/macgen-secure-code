class AuthenticationController < ApplicationController
  def login
    params.require(:email)
    params.require(:password)

    user = User.find_by(email: params[:email])

    if user&.authenticate(params[:password])
      render_json({ token: user.generate_jwt, message: "Login successful" })
    else
      render_json({ message: "Invalid email or password" }, :unauthorized)
    end
  end

  def register
    params.require(:email)
    params.require(:password)
    params.require(:name)

    if User.exists?(email: params[:email])
      render_json({ message: "Email already in use or invalid data" }, :bad_request)
      return
    end

    user = User.new(email: params[:email], password: params[:password], name: params[:name])

    if user.save
      render_json({ message: "Registration successful" }, :created)
    else
      render_json({ message: "Invalid data" }, :bad_request)
    end
  end
end