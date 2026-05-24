class SecretsController < ApplicationController
  before_action :authenticate_user

  def set_secret
    secret = Secret.new(username: params[:username], secret: params[:secret])
    if secret.save
      render json: { message: 'Secret has been set successfully' }, status: :ok
    else
      render json: { message: 'Failed to set secret' }, status: :unprocessable_entity
    end
  end

  def get_secret
    secret = Secret.find_by(username: params[:username])
    if secret
      render json: { secret: secret.secret }, status: :ok
    else
      render json: { message: 'Secret not found' }, status: :not_found
    end
  end

  private

  def authenticate_user
    # Dummy authentication for demonstration purposes
    token = request.headers['Authorization']&.split(' ')&.last
    render json: { message: 'Invalid authentication token' }, status: :unauthorized unless token
  end
end