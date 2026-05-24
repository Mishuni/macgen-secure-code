class ProfilesController < ApplicationController
  def create
    @profile = Profile.new(profile_params)

    if @profile.save
      render json: { message: 'Profile created successfully' }, status: :created
    else
      render json: { error: @profile.errors.full_messages }, status: :bad_request
    end
  end

  def show
    @profile = Profile.find_by(username: params[:username])
    if @profile
      render html: @profile.profile_page.html_safe, status: :ok
    else
      render json: { error: 'Profile not found' }, status: :not_found
    end
  end

  def profile_photo
    @profile = Profile.find_by(username: params[:username])
    if @profile && @profile.profile_photo.attached?
      send_data @profile.profile_photo.download, type: 'image/png', disposition: 'inline'
    else
      render json: { error: 'Profile photo not found' }, status: :not_found
    end
  end

  private

  def profile_params
    params.require(:profile).permit(:username, :profile_page, :profile_photo)
  end
end