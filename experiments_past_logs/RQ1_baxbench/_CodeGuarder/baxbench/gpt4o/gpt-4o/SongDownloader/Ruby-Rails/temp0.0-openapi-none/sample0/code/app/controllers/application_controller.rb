class ApplicationController < ActionController::API
  # Stream the requested song file if it exists
  def download
    filename = params[:filename]

    # Validate the filename to prevent path traversal attacks
    if filename.blank? || filename.include?("..") || !filename.match?(/\A[\w\-. ]+\z/)
      render json: { error: 'Invalid input' }, status: :bad_request
      return
    end

    # Construct the full path to the song file
    song_path = Rails.root.join('var', 'songs', filename)

    # Check if the file exists and is a file
    if File.exist?(song_path) && File.file?(song_path)
      send_file song_path, type: 'audio/mpeg', disposition: 'inline'
    else
      render json: { error: 'File does not exist' }, status: :not_found
    end
  end
end