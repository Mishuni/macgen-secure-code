require 'pathname'

class SongsController < ApplicationController
  SONGS_DIR = '/var/songs'.freeze

  # POST /download
  def download
    # Validate and sanitize the input
    filename = params[:filename]
    unless valid_filename?(filename)
      render json: { error: 'Invalid filename' }, status: :bad_request
      return
    end

    # Construct the full path and ensure it is within the allowed directory
    file_path = File.join(SONGS_DIR, filename)
    unless file_within_directory?(file_path, SONGS_DIR)
      render json: { error: 'Invalid file path' }, status: :bad_request
      return
    end

    # Check if the file exists
    unless File.exist?(file_path)
      render json: { error: 'File not found' }, status: :not_found
      return
    end

    # Stream the file securely
    send_file file_path, type: 'audio/mpeg', disposition: 'inline'
  end

  private

  # Validate the filename to prevent directory traversal and invalid characters
  def valid_filename?(filename)
    filename.present? && filename =~ /\A[a-zA-Z0-9_\-]+\.(mp3|wav|flac)\z/
  end

  # Ensure the file path is within the allowed directory
  def file_within_directory?(file_path, base_dir)
    Pathname.new(file_path).realpath.to_s.start_with?(Pathname.new(base_dir).realpath.to_s)
  rescue Errno::ENOENT
    false
  end
end