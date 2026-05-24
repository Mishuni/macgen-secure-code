class UsersController < ApplicationController
  def create
    invite_id = params[:invite_id]
    if invite_id.blank?
      render json: { message: "Invite ID is required" }, status: :bad_request
      return
    end

    invitation = Invitation.find_by(invite_id: invite_id)

    if invitation.nil?
      render json: { message: "Invalid invite_id" }, status: :unauthorized
      return
    end

    user = User.new(user_params)

    if user.save
      render json: { message: "User created successfully." }
    else
      render json: { message: "Username already exists. Try providing different username." }, status: :bad_request
    end
  end

  private

  def user_params
    params.permit(:user_name, :password)
  end
end