class FramesController < ApplicationController
  MAX_FILE_SIZE = 10.megabytes
  ALLOWED_FORMATS = ['.mp4', '.avi']

  def extract
    video_file = params[:video]
    frame_number = params[:frameNumber].to_i

    validate_input(video_file, frame_number)

    video_path = save_video(video_file)
    output_image_path = generate_output_image_path(video_file)

    extract_frame(video_path, frame_number, output_image_path)

    send_file output_image_path, type: 'image/png', disposition: 'inline'
  rescue ArgumentError => e
    render json: { error: e.message }, status: :unprocessable_entity
  ensure
    cleanup_files(video_path, output_image_path)
  end

  private

  def validate_input(video_file, frame_number)
    raise ArgumentError, "Invalid frame number" unless frame_number.is_a?(Integer) && frame_number >= 0
    raise ArgumentError, "File too large" if video_file.size > MAX_FILE_SIZE
    raise ArgumentError, "Invalid file type" unless ALLOWED_FORMATS.include?(File.extname(video_file.original_filename))
  end

  def save_video(video_file)
    video_path = Rails.root.join("tmp", video_file.original_filename)
    File.open(video_path, "wb") do |file|
      file.write(video_file.read)
    end
    video_path
  end

  def generate_output_image_path(video_file)
    output_image_path = Rails.root.join("tmp", "frame_#{Time.now.to_i}.png")
  end

  def extract_frame(video_path, frame_number, output_image_path)
    command = ["ffmpeg", "-i", video_path.to_s, "-vf", "select=eq(n\\,#{frame_number})", "-vframes", "1", output_image_path.to_s]
    system(*command)
    raise ArgumentError, "Frame at index #{frame_number} could not be found." unless File.exist?(output_image_path)
  end

  def cleanup_files(video_path, output_image_path)
    File.delete(video_path) if File.exist?(video_path)
    File.delete(output_image_path) if File.exist?(output_image_path)
  end
end