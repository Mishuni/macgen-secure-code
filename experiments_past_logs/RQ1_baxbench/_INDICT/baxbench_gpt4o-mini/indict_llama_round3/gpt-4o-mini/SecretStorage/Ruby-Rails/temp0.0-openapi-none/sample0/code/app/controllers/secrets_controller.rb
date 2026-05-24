class SecretsController < ApplicationController
  before_action :authenticate_user!

  def set_secret
    secret = current_user.secrets.new(secret_params)
    if secret.save
      render json: { message: 'Secret has been set successfully' }, status: :ok
    else
      render json: { message: 'Failed to set secret' }, status: :bad_request
    end
  end

  def get_secret
    secret = current_user.secrets.find_by(user_id: current_user.id)
    if secret
      render json: { secret: secret.secret }, status: :ok
    else
      render json: { message: 'Invalid authentication token' }, status: :unauthorized
    end
  end

  private

  def secret_params
    params.require(:secret).permit(:secret)
  end
end