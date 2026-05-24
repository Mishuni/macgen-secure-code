class UsersController < ApplicationController
  def create
    invitation = Invitation.find_by(invite_id: user_params[:invite_id])
    if invitation
      user = User.new(user_params.except(:invite_id))
      if user.save
        json_response({ message: "User created." })
      else
        json_response({ message: user.errors.full_messages.join(", ") }, :bad_request)
      end
    else
      json_response({ message: "Invalid invite_id" }, :unauthorized)
    end
  end

  private

  def user_params
    params.require(:user).permit(:invite_id, :user_name, :password)
  end
end