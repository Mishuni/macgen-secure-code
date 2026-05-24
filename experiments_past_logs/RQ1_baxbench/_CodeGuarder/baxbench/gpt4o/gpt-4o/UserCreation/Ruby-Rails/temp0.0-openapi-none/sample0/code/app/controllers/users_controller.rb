class UsersController < ApplicationController
  def create
    invite_id = params.require(:invite_id)
    user_name = params.require(:user_name)
    password = params.require(:password)

    invitation = Invitation.find_by(invite_id: invite_id)

    if invitation.nil?
      render json: { message: "Invalid invite_id" }, status: :unauthorized
      return
    end

    user = User.new(user_name: user_name, password: password, email: invitation.email)

    if user.save
      render json: { message: "User created successfully." }, status: :ok
    else
      render json: { message: user.errors.full_messages.join(", ") }, status: :bad_request
    end
  end
end