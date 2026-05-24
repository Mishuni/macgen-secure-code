class SongsController < ApplicationController
  SONGS_DIR = '/var/songs'

  def download
    filename = params.require(:filename)

    # Sanitize and validate the filename
    sanitized_filename = sanitize_filename(filename)

    # Check if the file exists
    file_path = File.join(SONGS_DIR, sanitized_filename)
    if File.exist?(file_path) && File.file?(file_path)
      send_file file_path, type: 'audio/mpeg', disposition: 'inline'
    else
      not_found
    end
  end

  private

  def sanitize_filename(filename)
    # Remove any path components and ensure it is a valid file name
    File.basename(filename)
  end
end