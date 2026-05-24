class InvitationsController < ApplicationController
  def invite_user
    email = params[:email]
    invitation = Invitation.find_or_create_by(email: email) do |inv|
      inv.invite_id = SecureRandom.uuid
    end

    render json: { invite_id: invitation.invite_id, message: "Invitation created or retrieved successfully." }, status: :ok
  end

  def create_user
    invite_id = params[:invite_id]
    user_name = params[:user_name]
    password = params[:password]

    invitation = Invitation.find_by(invite_id: invite_id)

    if invitation.nil?
      render json: { message: "Invalid invite_id" }, status: :unauthorized
      return
    end

    if User.exists?(user_name: user_name)
      render json: { message: "Username already exists. Try providing different username." }, status: :bad_request
      return
    end

    User.create!(user_name: user_name, password: password)
    render json: { message: "User created successfully." }, status: :ok
  end
end