require 'securerandom'

class ExtractController < ApplicationController
  def extract_frame
    # Validate input parameters
    unless params[:video].present? && params[:frameNumber].present?
      return render json: { error: "Missing required parameters" }, status: :bad_request
    end

    frame_number = params[:frameNumber].to_i
    if frame_number < 0
      return render json: { error: "Invalid frame number" }, status: :bad_request
    end

    # Save the uploaded video securely
    video_file = params[:video]
    video_path = Rails.root.join("tmp", "uploads", SecureRandom.uuid + File.extname(video_file.original_filename))
    FileUtils.mkdir_p(File.dirname(video_path))
    File.open(video_path, "wb") { |file| file.write(video_file.read) }

    # Generate a unique path for the extracted frame
    frame_path = Rails.root.join("tmp", "frames", SecureRandom.uuid + ".png")
    FileUtils.mkdir_p(File.dirname(frame_path))

    # Use ffmpeg to extract the frame
    begin
      ffmpeg_command = "ffmpeg -i #{Shellwords.escape(video_path.to_s)} -vf \"select=eq(n\\,#{frame_number})\" -vframes 1 #{Shellwords.escape(frame_path.to_s)}"
      system(ffmpeg_command)

      # Check if the frame was successfully extracted
      if File.exist?(frame_path) && File.size(frame_path) > 0
        send_file frame_path, type: "image/png", disposition: "inline"
      else
        render json: { error: "Frame at index #{frame_number} could not be found." }, status: :not_found
      end
    ensure
      # Clean up temporary files
      File.delete(video_path) if File.exist?(video_path)
      File.delete(frame_path) if File.exist?(frame_path)
    end
  end
end