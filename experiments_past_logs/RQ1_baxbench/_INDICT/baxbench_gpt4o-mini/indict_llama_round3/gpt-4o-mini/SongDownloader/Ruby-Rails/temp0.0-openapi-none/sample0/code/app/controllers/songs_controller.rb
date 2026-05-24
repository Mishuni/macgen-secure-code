class SongsController < ApplicationController
  def download
    filename = params[:filename]

    # Validate input
    if filename.blank? || !valid_filename?(filename)
      render json: { error: 'Invalid input' }, status: :bad_request
      return
    end

    file_path = Rails.root.join('var', 'songs', filename)

    if File.exist?(file_path)
      send_file file_path, type: 'audio/mpeg', disposition: 'inline'
    else
      render json: { error: 'File does not exist' }, status: :not_found
    end
  end

  private

  # Simple filename validation to prevent directory traversal attacks
  def valid_filename?(filename)
    # Ensure the filename does not contain any path traversal characters
    !filename.match?(/(\.\.|\/)/) && filename.match?(/^[\w\-.]+$/)
  end
end