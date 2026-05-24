class ImagesController < ApplicationController
  def upload
    if params[:file].present? && valid_image?(params[:file])
      image = Image.create(file: params[:file])
      render json: { id: image.id }, status: :ok
    else
      render json: { error: 'No valid file provided' }, status: :bad_request
    end
  rescue => e
    render json: { error: e.message }, status: :internal_server_error
  end

  def show
    image = Image.find_by(id: params[:imageId])
    if image
      send_data image.file.download, type: image.file.content_type, disposition: 'inline'
    else
      render json: { error: 'Image not found' }, status: :not_found
    end
  rescue => e
    render json: { error: e.message }, status: :internal_server_error
  end

  private

  def valid_image?(file)
    # Basic validation for image file types
    %w[image/jpeg image/png image/gif].include?(file.content_type)
  end
end