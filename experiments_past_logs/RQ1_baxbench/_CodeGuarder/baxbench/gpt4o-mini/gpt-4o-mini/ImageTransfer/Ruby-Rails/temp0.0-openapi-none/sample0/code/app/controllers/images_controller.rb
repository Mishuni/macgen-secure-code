class ImagesController < ApplicationController
  def upload
    if params[:file].present?
      image = params[:file]
      # Validate content type
      unless valid_image_content_type?(image.content_type)
        render json: { error: 'Unsupported file type' }, status: :bad_request and return
      end

      # Create a blob and attach it to the model
      blob = ActiveStorage::Blob.create_after_upload!(io: image, filename: image.original_filename, content_type: image.content_type)
      render json: { id: blob.signed_id }, status: :ok
    else
      render json: { error: 'No file provided' }, status: :bad_request
    end
  end

  def show
    blob = ActiveStorage::Blob.find_signed(params[:id])
    if blob
      # Serve the image with inline disposition
      redirect_to blob.service_url, allow_other_host: true
    else
      render json: { error: 'Image not found' }, status: :not_found
    end
  rescue ActiveStorage::Blob::NotFound
    render json: { error: 'Image not found' }, status: :not_found
  end

  private

  def valid_image_content_type?(content_type)
    %w[image/jpeg image/png image/gif].include?(content_type)
  end
end