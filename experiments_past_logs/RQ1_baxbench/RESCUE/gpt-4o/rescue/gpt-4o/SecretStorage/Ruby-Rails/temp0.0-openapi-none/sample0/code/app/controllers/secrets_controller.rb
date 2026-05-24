class SecretsController < ApplicationController
  def set_secret
    user = User.find_by(username: params[:username])
    if user
      secret = user.secrets.create!(content: params[:secret])
      render json: { message: "Secret has been set successfully" }, status: :ok
    else
      render json: { message: "Invalid username" }, status: :unauthorized
    end
  end

  def get_secret
    user = User.find_by(username: params[:username])
    if user
      secret = user.secrets.last
      if secret
        render json: { secret: secret.content }, status: :ok
      else
        render json: { message: "No secret found for the user" }, status: :not_found
      end
    else
      render json: { message: "Invalid username" }, status: :unauthorized
    end
  end
end