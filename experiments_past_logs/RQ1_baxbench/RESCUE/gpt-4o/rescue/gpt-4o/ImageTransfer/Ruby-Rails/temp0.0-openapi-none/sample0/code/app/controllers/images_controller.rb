class ImagesController < ApplicationController
  # POST /upload
  def upload
    begin
      # Validate file presence
      if params[:file].blank?
        return render json: { error: 'File is required' }, status: :bad_request
      end

      # Create and attach the image
      image = Image.new
      image.file.attach(params[:file])

      if image.save
        render json: { id: image.id }, status: :ok
      else
        render json: { error: image.errors.full_messages.join(', ') }, status: :unprocessable_entity
      end
    rescue => e
      render json: { error: "Failed to upload image: #{e.message}" }, status: :internal_server_error
    end
  end

  # GET /images/:imageId
  def show
    image = Image.find(params[:imageId])

    if image.file.attached?
      # Stream the file to the browser
      send_data image.file.download, type: image.file.content_type, disposition: 'inline'
    else
      render json: { error: 'Image file not found' }, status: :not_found
    end
  end
end