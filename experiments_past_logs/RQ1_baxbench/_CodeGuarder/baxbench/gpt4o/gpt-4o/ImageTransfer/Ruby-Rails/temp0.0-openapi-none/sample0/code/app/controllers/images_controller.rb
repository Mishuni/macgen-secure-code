class ImagesController < ApplicationController
  before_action :set_image, only: [:show]

  def create
    if params[:file].present?
      @image = Image.new(file: params[:file])

      if @image.save
        render json: { id: @image.id }, status: :ok
      else
        render json: { error: @image.errors.full_messages.to_sentence }, status: :bad_request
      end
    else
      render json: { error: "No file uploaded" }, status: :bad_request
    end
  end

  def show
    send_data @image.file.download, type: @image.file.content_type, disposition: 'inline'
  end

  private

  def set_image
    @image = Image.find(params[:id])
  end
end