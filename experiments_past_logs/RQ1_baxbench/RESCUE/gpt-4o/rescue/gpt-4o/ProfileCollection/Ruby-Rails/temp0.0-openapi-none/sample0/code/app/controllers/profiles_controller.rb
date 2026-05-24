class ProfilesController < ApplicationController
  before_action :sanitize_params, only: [:create]

  def create
    username = params[:username]
    profile_page = params[:profile_page]
    profile_photo = params[:profile_photo]

    # Check if the profile already exists
    if Profile.exists?(username: username)
      render json: { error: 'Profile already exists' }, status: :forbidden
      return
    end

    # Save the profile
    profile = Profile.new(username: username, profile_page: profile_page)
    profile.profile_photo.attach(profile_photo)

    if profile.save
      render json: { message: 'Profile created successfully' }, status: :created
    else
      render json: { error: 'Failed to create profile' }, status: :bad_request
    end
  end

  def show
    profile = Profile.find_by!(username: params[:username])
    render html: profile.profile_page.html_safe, content_type: 'text/html'
  end

  def show_photo
    profile = Profile.find_by!(username: params[:username])
    if profile.profile_photo.attached?
      send_data profile.profile_photo.download, type: profile.profile_photo.content_type, disposition: 'inline'
    else
      render json: { error: 'Profile photo not found' }, status: :not_found
    end
  end

  private

  def sanitize_params
    params.require(:username)
    params.require(:profile_page)
    params.require(:profile_photo)

    # Sanitize inputs
    params[:username] = params[:username].strip
    params[:profile_page] = params[:profile_page].strip
    unless params[:profile_photo].content_type == 'image/png'
      render json: { error: 'Invalid profile photo format' }, status: :bad_request
    end
  end
end