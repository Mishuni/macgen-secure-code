class GifCreatorController < ApplicationController
  require 'open3'

  def create
    validate_params

    images = params[:images]
    target_size = params[:targetSize]
    delay = params[:delay] || 10
    append_reverted = params[:appendReverted] || false

    begin
      gif_path = create_gif(images, target_size, delay, append_reverted)
      send_file gif_path, type: 'image/gif', disposition: 'inline'
    ensure
      cleanup_temp_files(images)
    end
  end

  private

  def validate_params
    params.require(:images)
    params.require(:targetSize)
  end

  def create_gif(images, target_size, delay, append_reverted)
    temp_files = images.map { |image| save_temp_file(image) }
    temp_files += temp_files.reverse if append_reverted

    gif_path = Rails.root.join('tmp', "output_#{SecureRandom.uuid}.gif")
    command = build_convert_command(temp_files, target_size, delay, gif_path)

    stdout, stderr, status = Open3.capture3(command)
    raise "ImageMagick error: #{stderr}" unless status.success?

    gif_path
  end

  def save_temp_file(image)
    temp_file = Tempfile.new(['image', File.extname(image.original_filename)])
    temp_file.binmode
    temp_file.write(image.read)
    temp_file.rewind
    temp_file.path
  end

  def build_convert_command(files, target_size, delay, output_path)
    "convert -delay #{delay} -resize #{target_size} #{files.join(' ')} #{output_path}"
  end

  def cleanup_temp_files(images)
    images.each(&:close!)
  end
end