class ProfilesController < ApplicationController
  before_action :set_profile, only: [:show, :photo]

  def create
    @profile = Profile.new(profile_params)

    if @profile.save
      render json: { message: 'Profile created successfully' }, status: :created
    else
      render json: { errors: @profile.errors.full_messages }, status: :unprocessable_entity
    end
  end

  def show
    render html: @profile.profile_page.html_safe
  end

  def photo
    if @profile.profile_photo.attached?
      send_data @profile.profile_photo.download, type: 'image/png', disposition: 'inline'
    else
      render json: { error: 'Profile photo not found' }, status: :not_found
    end
  end

  private

  def set_profile
    @profile = Profile.find_by(username: params[:username])
    render json: { error: 'Profile not found' }, status: :not_found unless @profile
  end

  def profile_params
    params.require(:profile).permit(:username, :profile_page, :profile_photo)
  end
end