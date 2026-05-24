class InvitationsController < ApplicationController
  def create
    email = params[:email]
    if email.blank?
      render json: { message: "Email is required" }, status: :bad_request
      return
    end

    invitation = Invitation.find_or_initialize_by(email: email)

    if invitation.new_record?
      invitation.invite_id = SecureRandom.uuid
      invitation.save!
    end

    render json: { invite_id: invitation.invite_id, message: "Invitation created or retrieved successfully." }
  end
end