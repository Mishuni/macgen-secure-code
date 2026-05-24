class ImagesController < ApplicationController
  before_action :set_image, only: [:show]

  def upload
    if params[:file].present? && valid_image?(params[:file])
      image = Image.create!(file: params[:file])
      render json: { id: image.id }, status: :ok
    else
      render json: { error: 'Invalid input' }, status: :bad_request
    end
  rescue => e
    render json: { error: e.message }, status: :internal_server_error
  end

  def show
    if @image.file.attached?
      redirect_to rails_blob_url(@image.file, disposition: "inline")
    else
      render json: { error: 'Image not found' }, status: :not_found
    end
  rescue => e
    render json: { error: e.message }, status: :internal_server_error
  end

  private

  def set_image
    @image = Image.find_by(id: params[:id])
    render json: { error: 'Image not found' }, status: :not_found unless @image
  end

  def valid_image?(file)
    file.content_type.start_with?('image/') && file.size <= 10.megabytes
  end
end