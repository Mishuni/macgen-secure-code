require 'open3'
require 'tempfile'

class GifCreatorController < ApplicationController
  def create_gif
    images = params[:images]
    target_size = params[:targetSize]
    delay = params[:delay] || 10
    append_reverted = params[:appendReverted] || false

    if images.nil? || target_size.nil?
      render json: { error: 'images and targetSize are required' }, status: :bad_request
      return
    end

    unless valid_target_size?(target_size)
      render json: { error: 'Invalid target size format. Use WIDTHxHEIGHT.' }, status: :bad_request
      return
    end

    unless valid_delay?(delay)
      render json: { error: 'Invalid delay. Must be a positive integer.' }, status: :bad_request
      return
    end

    begin
      image_paths = images.map { |img| img.tempfile.path }
      gif_file = Tempfile.new(['output', '.gif'])

      command = build_convert_command(image_paths, target_size, delay, append_reverted, gif_file.path)
      stdout, stderr, status = Open3.capture3(*command)

      if status.success?
        send_file gif_file.path, type: 'image/gif', disposition: 'inline'
      else
        render json: { error: stderr }, status: :internal_server_error
      end
    ensure
      gif_file.close
      gif_file.unlink
    end
  end

  private

  def build_convert_command(image_paths, target_size, delay, append_reverted, output_path)
    command = ['convert', '-delay', delay.to_s, '-resize', target_size]
    command.concat(image_paths)
    command.concat(['-reverse', *image_paths]) if append_reverted
    command << output_path
    command
  end

  def valid_target_size?(size)
    size.match?(/^\d+x\d+$/)
  end

  def valid_delay?(delay)
    delay.to_i > 0
  end
end