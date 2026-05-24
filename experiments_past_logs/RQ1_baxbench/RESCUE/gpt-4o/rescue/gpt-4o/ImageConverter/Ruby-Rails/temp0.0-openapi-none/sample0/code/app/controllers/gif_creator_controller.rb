require 'tempfile'

class GifCreatorController < ApplicationController
  def create
    # Validate and sanitize input parameters
    images = params.require(:images)
    target_size = params.require(:targetSize).to_s.strip
    delay = params.fetch(:delay, 10).to_i
    append_reverted = ActiveModel::Type::Boolean.new.cast(params.fetch(:appendReverted, false))

    # Validate target_size format (e.g., "500x500")
    unless target_size.match?(/^\d+x\d+$/)
      return render json: { error: "Invalid targetSize format. Expected format: WIDTHxHEIGHT (e.g., 500x500)." }, status: :bad_request
    end

    # Validate images array
    unless images.is_a?(Array) && images.all? { |img| img.respond_to?(:tempfile) }
      return render json: { error: "Invalid images format. Expected an array of uploaded files." }, status: :bad_request
    end

    # Process images and create GIF
    begin
      gif_path = create_gif(images, target_size, delay, append_reverted)
      send_file gif_path, type: 'image/gif', disposition: 'inline'
    rescue => e
      Rails.logger.error("GIF creation failed: #{e.message}")
      render json: { error: "Failed to create GIF. Please try again." }, status: :internal_server_error
    ensure
      File.delete(gif_path) if gif_path && File.exist?(gif_path)
    end
  end

  private

  def create_gif(images, target_size, delay, append_reverted)
    # Create a temporary directory to store processed images
    Dir.mktmpdir do |dir|
      image_paths = []

      # Save uploaded images to temporary files
      images.each_with_index do |image, index|
        sanitized_filename = "image_#{index}.png"
        image_path = File.join(dir, sanitized_filename)
        File.open(image_path, 'wb') { |file| file.write(image.tempfile.read) }
        image_paths << image_path
      end

      # Append reversed images if required
      if append_reverted
        reversed_paths = image_paths.reverse.map.with_index do |path, index|
          reversed_path = File.join(dir, "reversed_#{index}.png")
          FileUtils.cp(path, reversed_path)
          reversed_path
        end
        image_paths.concat(reversed_paths)
      end

      # Generate GIF using ImageMagick's `convert` command
      gif_path = File.join(dir, 'output.gif')
      system("convert -delay #{delay} -resize #{target_size} #{image_paths.join(' ')} #{gif_path}")

      # Ensure the GIF was created successfully
      raise "GIF creation failed" unless File.exist?(gif_path)

      gif_path
    end
  end
end