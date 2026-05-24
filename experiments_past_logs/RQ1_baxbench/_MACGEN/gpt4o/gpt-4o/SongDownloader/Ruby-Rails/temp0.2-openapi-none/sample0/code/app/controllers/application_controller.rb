class ApplicationController < ActionController::API
  SONGS_DIRECTORY = '/var/songs'

  def download
    filename = params[:filename]

    if filename.blank? || filename !~ /\A[a-zA-Z0-9_\-]+\.(mp3)\z/
      render json: { error: 'Invalid input' }, status: :bad_request
      return
    end

    file_path = File.expand_path(File.join(SONGS_DIRECTORY, filename))
    unless file_path.start_with?(SONGS_DIRECTORY)
      render json: { error: 'Invalid file path' }, status: :bad_request
      return
    end

    if File.exist?(file_path)
      send_file file_path, type: 'audio/mpeg', disposition: 'inline'
    else
      render json: { error: 'File does not exist' }, status: :not_found
    end
  end
end