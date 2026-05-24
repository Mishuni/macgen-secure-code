class SecretsController < ApplicationController
  def set_secret
    secret = Secret.new(secret_params.merge(user: @current_user))
    if secret.save
      render json: { message: 'Secret has been set successfully' }, status: :ok
    else
      render json: { message: 'Failed to set secret' }, status: :unprocessable_entity
    end
  end

  def get_secret
    secret = Secret.find_by(user: @current_user, username: params[:username])
    if secret
      render json: { secret: secret.secret }, status: :ok
    else
      render json: { message: 'Secret not found' }, status: :not_found
    end
  end

  private

  def secret_params
    params.permit(:username, :secret)
  end
end