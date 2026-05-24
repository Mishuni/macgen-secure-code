class InvitationsController < ApplicationController
  def create
    invitation = Invitation.new(invitation_params)

    if invitation.save
      render json: { invite_id: invitation.invite_id, message: 'Invitation email sent.' }, status: :ok
    else
      render json: { message: invitation.errors.full_messages.join(', ') }, status: :unprocessable_entity
    end
  end

  private

  def invitation_params
    params.require(:invitation).permit(:email)
  end
end