class SecretsController < ApplicationController
  def set_secret
    user = User.find_by(username: params[:username])
    if user
      user.secrets.create!(secret: params[:secret])
      render json: { message: "Secret has been set successfully" }, status: :ok
    else
      render json: { message: "Invalid authentication token" }, status: :unauthorized
    end
  end

  def get_secret
    user = User.find_by(username: params[:username])
    if user
      secret = user.secrets.last
      render json: { secret: secret.secret }, status: :ok
    else
      render json: { message: "Invalid authentication token" }, status: :unauthorized
    end
  end
end