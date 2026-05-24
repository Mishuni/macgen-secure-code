class RegistrationsController < ApplicationController
  def create
    user = User.new(user_params)
    if user.save
      json_response({ message: 'Registration successful' }, :created)
    else
      json_response({ message: 'Email already in use or invalid data' }, :bad_request)
    end
  end

  private

  def user_params
    params.require(:user).permit(:email, :password, :name)
  end
end