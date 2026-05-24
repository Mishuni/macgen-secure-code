class GifCreatorController < ApplicationController
  require 'tempfile'

  def create
    images = params[:images]
    target_size = params[:targetSize]
    delay = params[:delay] || 10
    append_reverted = params[:appendReverted] || false

    if images.blank? || target_size.blank?
      return render json: { error: 'Images and target size are required.' }, status: :bad_request
    end

    begin
      # Create a temporary file for the GIF
      Tempfile.create(['output', '.gif']) do |gif_file|
        # Prepare the command for ImageMagick
        command = ["convert"]
        images.each { |image| command << image.path }
        command << "-resize" << target_size
        command << "-delay" << delay.to_s
        command << gif_file.path

        # Append reverted images if required
        if append_reverted
          command << "&& convert"
          images.reverse.each { |image| command << image.path }
          command << "-resize" << target_size
          command << "-delay" << delay.to_s
          command << "-append" << gif_file.path
        end

        # Execute the command
        system(command.join(' '))

        # Send the GIF file as a response
        send_file gif_file.path, type: 'image/gif', disposition: 'attachment'
      end
    rescue => e
      render json: { error: e.message }, status: :internal_server_error
    end
  end
end