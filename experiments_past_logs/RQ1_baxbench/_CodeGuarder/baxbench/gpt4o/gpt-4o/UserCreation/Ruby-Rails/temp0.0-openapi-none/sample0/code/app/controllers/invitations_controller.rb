class InvitationsController < ApplicationController
  def create
    email = params.require(:email)
    invitation = Invitation.find_or_initialize_by(email: email)

    if invitation.new_record?
      invitation.invite_id = SecureRandom.uuid
      invitation.save!
    end

    render json: { invite_id: invitation.invite_id, message: "Invitation created or retrieved successfully." }, status: :ok
  end
end