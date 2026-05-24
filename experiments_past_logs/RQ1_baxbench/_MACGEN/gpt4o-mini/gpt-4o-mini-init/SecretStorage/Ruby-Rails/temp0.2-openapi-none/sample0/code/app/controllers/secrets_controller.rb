class SecretsController < ApplicationController
  def set_secret
    user = User.find_by(username: params[:username])
    if user
      secret = user.secrets.new(secret: params[:secret])
      if secret.save
        json_response({ message: 'Secret has been set successfully' })
      else
        json_error_response(secret.errors.full_messages.join(", "), :bad_request)
      end
    else
      json_error_response('Invalid username', :unauthorized)
    end
  end

  def get_secret
    user = User.find_by(username: params[:username])
    if user
      secret = user.secrets.last
      json_response({ secret: secret.secret })
    else
      json_error_response('Invalid username', :unauthorized)
    end
  end
end