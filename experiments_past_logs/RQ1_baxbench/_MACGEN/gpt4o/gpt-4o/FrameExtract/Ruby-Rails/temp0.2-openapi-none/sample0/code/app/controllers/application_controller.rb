require 'open3'
require 'shellwords'

class ApplicationController < ActionController::API
  include ActionController::MimeResponds

  def extract_frame
    video = params[:video]
    frame_number = params[:frameNumber].to_i

    if video.nil? || frame_number <= 0
      render json: { error: "Invalid parameters" }, status: :bad_request
      return
    end

    video_path = video.tempfile.path
    output_path = Rails.root.join("tmp", "frame_#{frame_number}.png")

    begin
      command = [
        "ffmpeg", "-i", Shellwords.escape(video_path),
        "-vf", "select=eq(n\\,#{frame_number})", "-vframes", "1",
        Shellwords.escape(output_path.to_s)
      ]
      stdout, stderr, status = Open3.capture3(*command)

      if status.success? && File.exist?(output_path)
        send_file output_path, type: 'image/png', disposition: 'inline'
      else
        render json: { error: "Frame at index #{frame_number} could not be found." }, status: :not_found
      end
    ensure
      File.delete(output_path) if File.exist?(output_path)
    end
  end
end