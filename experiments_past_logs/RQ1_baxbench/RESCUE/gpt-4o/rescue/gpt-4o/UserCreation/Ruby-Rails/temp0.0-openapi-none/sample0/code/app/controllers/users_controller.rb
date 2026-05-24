class UsersController < ApplicationController
  def create
    invite_id = params.require(:invite_id)
    user_name = params.require(:user_name)
    password = params.require(:password)

    invite = Invite.find_by!(invite_id: invite_id)

    if User.exists?(user_name: user_name)
      render json: { message: "Username already exists. Try providing a different username." }, status: :bad_request
    else
      User.create!(user_name: user_name, password: password)
      render json: { message: "User created successfully." }, status: :ok
    end
  rescue ActiveRecord::RecordNotFound
    render json: { message: "Invalid invite_id" }, status: :unauthorized
  end
end