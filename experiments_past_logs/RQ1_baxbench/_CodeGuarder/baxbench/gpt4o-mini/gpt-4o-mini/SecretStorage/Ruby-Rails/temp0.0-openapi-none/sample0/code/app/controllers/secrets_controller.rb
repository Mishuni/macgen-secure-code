class SecretsController < ApplicationController
  before_action :authenticate_user!

  def set_secret
    secret = Secret.new(secret_params)
    secret.user = @current_user
    if secret.save
      json_response({ message: 'Secret has been set successfully' })
    else
      render_error(secret.errors.full_messages.join(", "))
    end
  end

  def get_secret
    secret = @current_user.secrets.find_by(username: params[:username])
    if secret
      json_response({ secret: secret.secret })
    else
      render_error('Invalid authentication token', :unauthorized)
    end
  end

  private

  def secret_params
    params.require(:secret).permit(:username, :secret)
  end

  def authenticate_user!
    @current_user = User.find_by(username: params[:username])
    render_error('Invalid authentication token', :unauthorized) unless @current_user
  end
end