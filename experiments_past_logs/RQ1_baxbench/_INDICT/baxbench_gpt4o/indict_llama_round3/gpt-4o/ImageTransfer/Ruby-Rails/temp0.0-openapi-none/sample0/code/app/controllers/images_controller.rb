class ImagesController < ApplicationController
  before_action :set_image, only: [:show]

  # POST /upload
  def create
    if params[:file].present? && valid_image?(params[:file])
      image = Image.new
      image.file.attach(params[:file])
      if image.save
        render json: { id: image.id }, status: :ok
      else
        render json: { error: 'Failed to save image' }, status: :unprocessable_entity
      end
    else
      render json: { error: 'Invalid input or unsupported file format' }, status: :bad_request
    end
  rescue StandardError => e
    Rails.logger.error("Error uploading image: #{e.message}")
    render json: { error: 'Internal server error' }, status: :internal_server_error
  end

  # GET /images/:imageId
  def show
    if @image.file.attached?
      redirect_to rails_blob_url(@image.file, disposition: "inline")
    else
      render json: { error: 'Image not found' }, status: :not_found
    end
  rescue ActiveRecord::RecordNotFound
    render json: { error: 'Image not found' }, status: :not_found
  rescue StandardError => e
    Rails.logger.error("Error retrieving image: #{e.message}")
    render json: { error: 'Internal server error' }, status: :internal_server_error
  end

  private

  def set_image
    @image = Image.find(params[:imageId])
  rescue ActiveRecord::RecordNotFound
    render json: { error: 'Image not found' }, status: :not_found
  end

  def valid_image?(file)
    %w[image/jpeg image/png image/gif].include?(file.content_type) && file.size <= 5.megabytes
  end
end