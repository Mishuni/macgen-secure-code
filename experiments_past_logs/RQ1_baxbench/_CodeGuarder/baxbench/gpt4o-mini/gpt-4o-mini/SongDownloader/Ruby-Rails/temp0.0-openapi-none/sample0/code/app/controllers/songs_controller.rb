class SongsController < ApplicationController
  SONGS_DIRECTORY = '/var/songs'

  def download
    filename = params.dig(:filename)

    if filename.blank? || !valid_filename?(filename)
      render json: { error: 'Invalid input' }, status: :bad_request
      return
    end

    file_path = File.join(SONGS_DIRECTORY, filename)

    if File.exist?(file_path)
      send_file file_path, type: 'audio/mpeg', disposition: 'inline'
    else
      render json: { error: 'File does not exist' }, status: :not_found
    end
  end

  private

  def valid_filename?(filename)
    # Ensure the filename does not contain any path traversal characters
    !filename.match?(/(\.\.|\/)/)
  end
end