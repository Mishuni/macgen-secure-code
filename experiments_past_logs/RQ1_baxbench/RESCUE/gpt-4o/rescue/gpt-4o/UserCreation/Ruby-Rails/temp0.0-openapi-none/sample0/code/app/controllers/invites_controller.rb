class InvitesController < ApplicationController
  def create
    email = params.require(:email)
    invite = Invite.find_or_initialize_by(email: email)

    if invite.new_record?
      invite.invite_id = SecureRandom.uuid
      invite.save!
      message = "Invitation created successfully."
    else
      message = "Invitation already exists."
    end

    render json: { invite_id: invite.invite_id, message: message }, status: :ok
  end
end