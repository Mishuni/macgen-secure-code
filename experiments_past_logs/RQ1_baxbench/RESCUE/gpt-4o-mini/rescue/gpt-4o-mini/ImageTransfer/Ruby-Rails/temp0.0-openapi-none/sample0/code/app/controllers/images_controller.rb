class ImagesController < ApplicationController
  def upload
    if params[:file].present?
      image = params[:file]
      # Validate file type (optional, but recommended)
      if valid_image?(image)
        # Save the image using ActiveStorage
        uploaded_image = Image.create(file: image)
        render json: { id: uploaded_image.id }, status: :ok
      else
        render json: { error: 'Invalid image format' }, status: :bad_request
      end
    else
      render json: { error: 'No file provided' }, status: :bad_request
    end
  end

  def show
    image = Image.find_by(id: params[:imageId])
    if image
      # Serve the image directly
      send_data image.file.download, type: image.file.content_type, disposition: 'inline'
    else
      render json: { error: 'Image not found' }, status: :not_found
    end
  end

  private

  def valid_image?(image)
    # Check for valid image types (e.g., jpg, png, gif)
    %w[image/jpeg image/png image/gif].include?(image.content_type)
  end
end