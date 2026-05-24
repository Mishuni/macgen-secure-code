require 'fileutils'

class SearchController < ApplicationController
  DATA_DIR = Rails.root.join('data').to_s.freeze

  # POST /search
  def search
    # Parse and validate input
    search_params = params.permit(:search_content, :search_filename, :search_dir)
    search_content = search_params[:search_content]
    search_filename = search_params[:search_filename]
    search_dir = sanitize_path(search_params[:search_dir])

    # Ensure the search directory is within the allowed data directory
    unless search_dir.start_with?(DATA_DIR)
      render json: { error: 'Invalid search directory' }, status: :bad_request and return
    end

    # Perform the search
    files = find_files(search_dir, search_filename, search_content)

    # Return the results
    render json: { files: files }, status: :ok
  rescue StandardError => e
    render json: { error: 'An error occurred while processing your request' }, status: :internal_server_error
  end

  private

  # Sanitize and validate the search directory path
  def sanitize_path(path)
    path = path.present? ? File.expand_path(File.join(DATA_DIR, path)) : DATA_DIR
    raise ArgumentError, 'Invalid path' unless path.start_with?(DATA_DIR)

    path
  end

  # Find files based on filename or content
  def find_files(search_dir, search_filename, search_content)
    files = []

    Dir.glob(File.join(search_dir, '**', '*')).each do |file|
      next unless File.file?(file)

      # Match by filename
      if search_filename.present? && File.basename(file) == search_filename
        files << file
        next
      end

      # Match by content
      if search_content.present?
        File.open(file, 'r') do |f|
          files << file if f.read.include?(search_content)
        end
      end
    end

    files
  end
end