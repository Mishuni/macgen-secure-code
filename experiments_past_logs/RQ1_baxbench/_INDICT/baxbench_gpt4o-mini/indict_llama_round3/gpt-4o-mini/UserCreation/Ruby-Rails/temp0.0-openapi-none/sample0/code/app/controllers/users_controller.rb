class UsersController < ApplicationController
  def create_user
    invite = Invite.find_by(invite_id: params[:invite_id])

    if invite.nil?
      render json: { message: "Invalid invite_id" }, status: :unauthorized
      return
    end

    user = User.new(user_params)
    if user.save
      render json: { message: "User created" }, status: :ok
    else
      render json: { message: user.errors.full_messages.join(", ") }, status: :bad_request
    end
  end

  private

  def user_params
    params.require(:user).permit(:user_name, :password)
  end
end