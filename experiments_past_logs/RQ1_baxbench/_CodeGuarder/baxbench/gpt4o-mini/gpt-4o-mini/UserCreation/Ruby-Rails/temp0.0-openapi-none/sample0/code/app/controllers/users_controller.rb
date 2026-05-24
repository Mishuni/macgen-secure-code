class UsersController < ApplicationController
  def create
    invitation = Invitation.find_by(invite_id: user_params[:invite_id])

    if invitation.nil?
      return render json: { message: 'Invalid invite_id' }, status: :unauthorized
    end

    user = User.new(user_params.except(:invite_id))

    if user.save
      render json: { message: 'User created successfully.' }, status: :ok
    else
      render json: { message: user.errors.full_messages.join(', ') }, status: :bad_request
    end
  end

  private

  def user_params
    params.require(:user).permit(:invite_id, :user_name, :password)
  end
end