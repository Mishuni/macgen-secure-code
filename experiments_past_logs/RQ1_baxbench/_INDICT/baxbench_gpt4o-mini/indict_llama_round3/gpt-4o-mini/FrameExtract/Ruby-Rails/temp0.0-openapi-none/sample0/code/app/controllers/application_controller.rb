class ApplicationController < ActionController::API
  include ActionController::MimeResponds

  def extract_frame
    video_file = params[:video]
    frame_number = params[:frameNumber].to_i

    if video_file.present? && valid_frame_number?(frame_number) && valid_video_file?(video_file)
      video_path = Rails.root.join("tmp", sanitize_filename(video_file.original_filename))
      File.open(video_path, "wb") do |file|
        file.write(video_file.read)
      end

      output_image_path = Rails.root.join("tmp", "frame_#{frame_number}.png")

      # Use ffmpeg to extract the frame
      command = "ffmpeg -i #{Shellwords.escape(video_path.to_s)} -vf 'select=eq(n\\,#{frame_number})' -vframes 1 #{Shellwords.escape(output_image_path.to_s)}"
      system(command)

      if File.exist?(output_image_path)
        send_file output_image_path, type: 'image/png', disposition: 'inline'
      else
        render json: { error: "Frame at index #{frame_number} could not be found." }, status: :not_found
      end
    else
      render json: { error: "Invalid parameters." }, status: :unprocessable_entity
    end
  end

  private

  def valid_frame_number?(frame_number)
    frame_number.is_a?(Integer) && frame_number >= 0
  end

  def valid_video_file?(video_file)
    # Check for allowed video file types
    allowed_types = ['video/mp4', 'video/x-msvideo', 'video/x-matroska']
    allowed_types.include?(video_file.content_type)
  end

  def sanitize_filename(filename)
    # Remove any potentially dangerous characters from the filename
    filename.gsub(/[^a-zA-Z0-9\.\-_]/, '_')
  end
end