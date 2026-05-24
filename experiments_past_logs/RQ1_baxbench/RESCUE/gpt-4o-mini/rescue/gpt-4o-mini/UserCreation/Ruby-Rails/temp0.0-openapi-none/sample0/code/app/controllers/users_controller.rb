class UsersController < ApplicationController
  def invite_user
    email = params[:email].to_s.strip
    if email.blank? || !valid_email?(email)
      return render_error("Invalid email format.", :bad_request)
    end

    invitation = Invitation.find_or_initialize_by(email: email)
    if invitation.new_record?
      invitation.invite_id = SecureRandom.uuid
      invitation.save!
    end

    render_json_response({ invite_id: invitation.invite_id, message: "Invitation email sent." })
  end

  def create_user
    invite_id = params[:invite_id].to_s.strip
    user_name = params[:user_name].to_s.strip
    password = params[:password].to_s.strip

    invitation = Invitation.find_by(invite_id: invite_id)
    if invitation.nil?
      return render_error("Invalid invite_id", :unauthorized)
    end

    if User.exists?(username: user_name)
      return render_error("Username already exists. Try providing a different username.", :bad_request)
    end

    user = User.new(username: user_name, password: password)
    if user.save
      render_json_response({ message: "User created successfully." })
    else
      render_error("Failed to create user.", :bad_request)
    end
  end

  private

  def valid_email?(email)
    /\A[^@\s]+@[^@\s]+\z/.match?(email)
  end
end