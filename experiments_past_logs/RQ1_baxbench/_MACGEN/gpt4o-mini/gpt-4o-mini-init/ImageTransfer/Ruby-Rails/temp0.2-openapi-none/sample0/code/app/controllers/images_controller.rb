class ImagesController < ApplicationController
  def upload
    image = Image.new(image_params)
    if image.save
      render json: { id: image.id }, status: :ok
    else
      render json: { error: image.errors.full_messages.join(", ") }, status: :bad_request
    end
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

  def image_params
    params.require(:file).permit(:file)
  end
end