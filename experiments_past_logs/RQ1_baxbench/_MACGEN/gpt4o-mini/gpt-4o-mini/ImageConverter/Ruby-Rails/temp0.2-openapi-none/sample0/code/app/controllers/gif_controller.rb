class GifController < ApplicationController
  def create
    images = params[:images]
    target_size = params[:targetSize]
    delay = params[:delay] || 10
    append_reverted = params[:appendReverted] || false

    if images.blank? || target_size.blank? || !valid_target_size?(target_size) || !valid_delay?(delay)
      return render json: { error: 'Images, target size, and a valid delay are required.' }, status: :bad_request
    end

    begin
      image_files = images.map { |image| image.tempfile.path }
      gif_path = create_gif(image_files, target_size, delay, append_reverted)
      send_file gif_path, type: 'image/gif', disposition: 'attachment'
    rescue => e
      render json: { error: "An error occurred. Please try again later." }, status: :internal_server_error
    end
  end

  private

  def valid_target_size?(size)
    size.match?(/\A\d+x\d+\z/)
  end

  def valid_delay?(delay)
    (delay.is_a?(Integer) && delay.positive?) || (delay.is_a?(String) && delay.to_i.positive?)
  end

  def create_gif(image_files, target_size, delay, append_reverted)
    gif_file = "#{Rails.root}/tmp/output.gif"
    command = ["convert", *image_files, "-resize", target_size, "-delay", delay.to_s]
    command << "-reverse" if append_reverted
    command << gif_file
    system(*command)
    gif_file
  end
end