class UsersController < ApplicationController
  require 'securerandom'

  def invite_user
    email = params[:email]
    if email.blank? || !email.match?(URI::MailTo::EMAIL_REGEXP)
      render json: { message: "Invalid email format" }, status: :bad_request
      return
    end

    user_invitation = UserInvitation.find_or_initialize_by(email: email)

    if user_invitation.new_record?
      user_invitation.invite_id = SecureRandom.uuid
      user_invitation.save!
    end

    render json: { message: "If the email is valid, an invitation has been sent." }, status: :ok
  end

  def create_user
    invite_id = params[:invite_id]
    user_name = params[:user_name]
    password = params[:password]

    if user_name.blank? || password.blank?
      render json: { message: "Username and password cannot be blank" }, status: :bad_request
      return
    end

    unless password.match?(/\A(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}\z/)
      render json: { message: "Password must be at least 8 characters long, include one uppercase letter, one lowercase letter, and one digit." }, status: :bad_request
      return
    end

    user_invitation = UserInvitation.find_by(invite_id: invite_id)

    if user_invitation.nil?
      render json: { message: "Invalid invite_id" }, status: :unauthorized
      return
    end

    if User.exists?(user_name: user_name)
      render json: { message: "Username already exists. Try providing a different username." }, status: :bad_request
      return
    end

    User.create!(user_name: user_name, password: password)
    render json: { message: "User created successfully." }, status: :ok
  end
end