class InvitationsController < ApplicationController
  def create
    invitation = Invitation.find_or_initialize_by(email: invitation_params[:email])
    if invitation.new_record?
      invitation.save
      json_response({ invite_id: invitation.invite_id, message: "Invitation email sent." })
    else
      json_response({ invite_id: invitation.invite_id, message: "Invitation already exists." })
    end
  end

  private

  def invitation_params
    params.require(:invitation).permit(:email)
  end
end