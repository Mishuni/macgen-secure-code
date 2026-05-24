class SongsController < ApplicationController
  require 'pathname'

  SONGS_DIRECTORY = '/var/songs'

  def download
    filename = params[:filename]

    unless valid_filename?(filename)
      render json: { error: 'Invalid input' }, status: :bad_request
      return
    end

    file_path = Pathname.new(SONGS_DIRECTORY).join(filename).cleanpath

    unless file_path.to_s.start_with?(SONGS_DIRECTORY) && File.exist?(file_path)
      render json: { error: 'File does not exist' }, status: :not_found
      return
    end

    send_file file_path, type: 'audio/mpeg', disposition: 'inline'
  end

  private

  def valid_filename?(filename)
    filename =~ /\A[\w\-. ]+\.(mp3|wav|ogg)\z/i
  end
end