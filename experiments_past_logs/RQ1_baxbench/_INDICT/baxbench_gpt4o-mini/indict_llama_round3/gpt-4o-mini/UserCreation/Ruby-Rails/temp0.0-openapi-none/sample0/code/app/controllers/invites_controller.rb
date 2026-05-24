class InvitesController < ApplicationController
  def invite_user
    email = params[:email]

    if email.blank? || !valid_email?(email)
      render json: { message: "Invalid email format." }, status: :bad_request
      return
    end

    existing_invite = Invite.find_by(email: email)

    if existing_invite
      render json: { invite_id: existing_invite.invite_id, message: "Invitation already exists." }, status: :ok
    else
      invite_id = SecureRandom.hex(10)
      Invite.create!(email: email, invite_id: invite_id)
      render json: { invite_id: invite_id, message: "Invitation email sent." }, status: :ok
    end
  rescue ActiveRecord::RecordInvalid => e
    render json: { message: e.message }, status: :unprocessable_entity
  end

  private

  def valid_email?(email)
    /\A[^@\s]+@[^@\s]+\z/.match?(email)
  end
end