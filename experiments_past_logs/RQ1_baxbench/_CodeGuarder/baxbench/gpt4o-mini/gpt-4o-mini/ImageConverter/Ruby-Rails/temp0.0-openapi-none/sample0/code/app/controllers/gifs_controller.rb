class GifsController < ApplicationController
  def create
    images = params[:images]
    target_size = params[:targetSize]
    delay = params[:delay] || 10
    append_reverted = params[:appendReverted] || false

    if images.blank? || target_size.blank?
      render json: { error: 'Images and target size are required.' }, status: :bad_request and return
    end

    begin
      # Create a temporary directory to store uploaded images
      Dir.mktmpdir do |dir|
        image_paths = []

        images.each do |image|
          # Save the uploaded image to the temporary directory
          file_path = File.join(dir, image.original_filename)
          File.open(file_path, 'wb') do |f|
            f.write(image.read)
          end
          image_paths << file_path
        end

        # Construct the command for ImageMagick
        gif_path = File.join(dir, 'output.gif')
        command = ["convert", *image_paths, "-resize", target_size, "-delay", delay.to_s, gif_path]

        # Append the reverted images if specified
        if append_reverted
          command += image_paths.reverse
        end

        # Execute the command
        system(*command)

        # Send the GIF back to the client
        send_file gif_path, type: 'image/gif', disposition: 'attachment'
      end
    rescue => e
      render json: { error: 'Failed to create GIF: ' + e.message }, status: :internal_server_error
    end
  end
end