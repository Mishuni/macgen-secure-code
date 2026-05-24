class ProfilesController < ApplicationController
  before_action :set_profile, only: [:show, :profile_photo]

  def create
    username = params[:username].strip
    profile_page = params[:profile_page]
    profile_photo = params[:profile_photo]

    if Profile.exists?(username: username)
      render_json({ error: 'Profile already exists, creation forbidden' }, :forbidden)
      return
    end

    sanitized_profile_page = sanitize(profile_page)
    profile = Profile.new(username: username, profile_page: sanitized_profile_page)

    if profile.save
      # Handle file upload for profile photo
      if profile_photo.present?
        profile.photo.attach(profile_photo)
      end
      render_json({ message: 'Profile created successfully' }, :created)
    else
      render_json({ error: 'Invalid input' }, :bad_request)
    end
  end

  def show
    render_json({ username: @profile.username, profile_page: @profile.profile_page }, :ok)
  end

  def profile_photo
    if @profile.photo.attached?
      render @profile.photo, content_type: 'image/png'
    else
      render_json({ error: 'Profile photo not found' }, :not_found)
    end
  end

  private

  def set_profile
    @profile = Profile.find_by(username: params[:username])
    render_json({ error: 'Profile not found' }, :not_found) unless @profile
  end

  def sanitize(html)
    ActionController::Base.helpers.sanitize(html)
  end
end