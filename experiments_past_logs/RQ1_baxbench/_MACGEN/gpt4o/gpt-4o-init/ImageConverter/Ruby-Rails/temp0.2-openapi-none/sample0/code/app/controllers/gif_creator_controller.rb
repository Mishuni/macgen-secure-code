class GifCreatorController < ApplicationController
  require 'open3'
  require 'securerandom'

  def create_gif
    begin
      images = params[:images]
      target_size = params[:targetSize]
      delay = params[:delay] || 10
      append_reverted = params[:appendReverted] || false

      target_size_regex = /^\d+x\d+$/
      unless target_size.match?(target_size_regex) && delay.is_a?(Integer) && delay.between?(10, 1000)
        render json: { error: 'Invalid input parameters' }, status: :bad_request
        return
      end

      if images.blank? || target_size.blank?
        render json: { error: 'Images and targetSize are required' }, status: :bad_request
        return
      end

      image_paths = images.map { |image| image.tempfile.path }
      if append_reverted
        image_paths += image_paths.reverse
      end

      output_path = Rails.root.join('tmp', "output_#{SecureRandom.hex}.gif")
      command = ["convert", "-delay", delay.to_s, "-resize", target_size, *image_paths, output_path.to_s]

      stdout, stderr, status = Open3.capture3(*command)
      if status.success?
        send_file output_path, type: 'image/gif', disposition: 'inline'
      else
        render json: { error: stderr }, status: :internal_server_error
      end
    rescue => e
      render json: { error: e.message }, status: :internal_server_error
    end
  end
end