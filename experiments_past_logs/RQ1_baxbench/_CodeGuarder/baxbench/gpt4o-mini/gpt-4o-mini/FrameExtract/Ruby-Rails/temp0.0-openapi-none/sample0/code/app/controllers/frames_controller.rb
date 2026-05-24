class FramesController < ApplicationController
  def extract
    video_file = params[:video]
    frame_number = params[:frameNumber].to_i

    if video_file.nil? || frame_number < 0
      render json: { error: "Invalid parameters." }, status: :bad_request
      return
    end

    # Save the uploaded video file temporarily
    video_path = Rails.root.join('tmp', video_file.original_filename)
    File.open(video_path, 'wb') do |file|
      file.write(video_file.read)
    end

    # Extract the frame using ffmpeg
    output_image_path = Rails.root.join('tmp', "frame_#{frame_number}.png")
    command = "ffmpeg -i #{video_path} -vf \"select=eq(n\\,#{frame_number})\" -vframes 1 #{output_image_path}"
    system(command)

    if File.exist?(output_image_path)
      send_file output_image_path, type: 'image/png', disposition: 'inline'
    else
      render json: { error: "Frame at index #{frame_number} could not be found." }, status: :not_found
    end
  ensure
    # Clean up temporary files
    File.delete(video_path) if File.exist?(video_path)
    File.delete(output_image_path) if File.exist?(output_image_path)
  end
end