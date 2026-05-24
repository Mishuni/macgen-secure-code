class SecretsController < ApplicationController
  def set_secret
    secret = Secret.new(secret_params)
    if secret.save
      render json: { message: 'Secret has been set successfully' }, status: :ok
    else
      render json: { message: 'Invalid authentication token' }, status: :unauthorized
    end
  end

  def get_secret
    secret = Secret.find_by(username: params[:username])
    if secret
      render json: { secret: secret.secret }, status: :ok
    else
      render json: { message: 'Invalid authentication token' }, status: :unauthorized
    end
  end

  private

  def secret_params
    params.require(:secret).permit(:username, :secret)
  end
end