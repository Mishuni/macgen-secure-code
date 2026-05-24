class GifController < ApplicationController
  def create
    images = params[:images]
    target_size = params[:targetSize]
    delay = params[:delay].to_i || 10
    append_reverted = ActiveModel::Type::Boolean.new.cast(params[:appendReverted]) || false

    if images.blank? || target_size.blank?
      render json: { error: 'Images and target size are required.' }, status: :bad_request and return
    end

    begin
      image_files = images.map { |image| image.tempfile.path }
      gif_path = create_gif(image_files, target_size, delay, append_reverted)

      send_file gif_path, type: 'image/gif', disposition: 'attachment'
    rescue => e
      render json: { error: e.message }, status: :internal_server_error
    end
  end

  private

  def create_gif(image_files, target_size, delay, append_reverted)
    gif_path = Rails.root.join('tmp', "output.gif")

    # Prepare the command for ImageMagick
    command = ["convert", "-delay", delay.to_s, "-resize", target_size]
    command.concat(image_files)

    if append_reverted
      command.concat(image_files.reverse)
    end

    command << gif_path.to_s

    # Execute the command safely
    system(*command)

    gif_path
  end
end