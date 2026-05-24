class SongsController < ApplicationController
  SONGS_DIRECTORY = '/var/songs'
  ALLOWED_EXTENSIONS = %w[.mp3 .wav .flac]

  def download
    filename = params[:filename]

    if filename.blank?
      render json: { error: 'Invalid input' }, status: :bad_request
      return
    end

    # Sanitize the filename to prevent directory traversal attacks
    sanitized_filename = File.basename(filename)

    # Check for allowed file extensions
    unless ALLOWED_EXTENSIONS.include?(File.extname(sanitized_filename))
      render json: { error: 'Invalid file type' }, status: :bad_request
      return
    end

    file_path = File.join(SONGS_DIRECTORY, sanitized_filename)

    if File.exist?(file_path)
      send_file file_path, type: 'audio/mpeg', disposition: 'inline'
    else
      render json: { error: 'File does not exist' }, status: :not_found
    end
  end
end