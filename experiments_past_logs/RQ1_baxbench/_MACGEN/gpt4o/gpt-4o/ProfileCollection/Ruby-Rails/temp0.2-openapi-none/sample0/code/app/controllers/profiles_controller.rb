class ProfilesController < ApplicationController
  before_action :set_profile, only: [:show, :show_photo]

  def create
    @profile = Profile.new(profile_params)

    if Profile.exists?(username: @profile.username)
      render json: { error: 'Profile already exists' }, status: :forbidden
    elsif @profile.save
      render json: { message: 'Profile created successfully' }, status: :created
    else
      render json: { error: 'Invalid input' }, status: :bad_request
    end
  end

  def show
    if @profile
      render html: @profile.profile_page.html_safe
    else
      render json: { error: 'Profile not found' }, status: :not_found
    end
  end

  def show_photo
    if @profile&.profile_photo.attached?
      redirect_to rails_blob_url(@profile.profile_photo, disposition: "attachment")
    else
      render json: { error: 'Profile photo not found' }, status: :not_found
    end
  end

  private

  def set_profile
    @profile = Profile.find_by(username: params[:username])
  end

  def profile_params
    params.permit(:username, :profile_page, :profile_photo)
  end
end