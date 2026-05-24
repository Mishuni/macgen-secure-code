class UsersController < ApplicationController
  def register
    user = User.new(user_params)
    if user.save
      json_response({ message: 'Registration successful' }, :created)
    else
      json_error_response(user.errors.full_messages.join(", "), :bad_request)
    end
  end

  def login
    user = User.find_by(email: params[:email])
    if user&.authenticate(params[:password])
      json_response({ message: 'Login successful' })
    else
      json_error_response('Invalid email or password', :unauthorized)
    end
  end

  private

  def user_params
    params.require(:user).permit(:email, :username, :password)
  end
end