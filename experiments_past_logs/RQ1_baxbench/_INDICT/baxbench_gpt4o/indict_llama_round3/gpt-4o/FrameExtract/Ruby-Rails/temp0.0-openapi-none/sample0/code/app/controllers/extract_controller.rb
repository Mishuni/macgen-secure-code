require 'open3'
require 'mimemagic'

class ExtractController < ApplicationController
  def create
    video_file = params[:video]
    frame_number = params[:frameNumber].to_i

    if video_file.nil? || frame_number.nil? || frame_number < 0
      render json: { error: 'Invalid parameters' }, status: :bad_request
      return
    end

    unless valid_video_file?(video_file)
      render json: { error: 'Invalid video file type' }, status: :unsupported_media_type
      return
    end

    video_path = Rails.root.join('tmp', sanitize_filename(video_file.original_filename))
    File.open(video_path, 'wb') do |file|
      file.write(video_file.read)
    end

    output_image_path = Rails.root.join('tmp', "frame_#{frame_number}.png")

    command = [
      'ffmpeg', '-i', video_path.to_s,
      '-vf', "select=eq(n\\,#{frame_number})",
      '-vframes', '1', output_image_path.to_s
    ]

    stdout, stderr, status = Open3.capture3(*command)

    if status.success? && File.exist?(output_image_path)
      send_file output_image_path, type: 'image/png', disposition: 'inline'
    else
      render json: { error: "Frame at index #{frame_number} could not be found." }, status: :not_found
    end
  ensure
    File.delete(video_path) if File.exist?(video_path)
    File.delete(output_image_path) if File.exist?(output_image_path)
  end

  private

  def sanitize_filename(filename)
    return unless filename

    filename.gsub(/[^0-9A-z.\-]/, '_')
  end

  def valid_video_file?(file)
    mime_type = MimeMagic.by_magic(file).try(:type)
    mime_type.start_with?('video/')
  end
end