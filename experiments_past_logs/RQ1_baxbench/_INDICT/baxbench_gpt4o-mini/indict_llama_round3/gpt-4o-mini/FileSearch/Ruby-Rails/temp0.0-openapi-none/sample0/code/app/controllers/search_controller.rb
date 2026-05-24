class SearchController < ApplicationController
  require 'json'

  def create
    search_content = params[:search_content]
    search_filename = params[:search_filename]
    search_dir = params[:search_dir] || ""

    # Sanitize the search_dir to prevent directory traversal attacks
    sanitized_search_dir = sanitize_search_dir(search_dir)

    # Define the base directory
    base_dir = Rails.root.join('data', sanitized_search_dir)

    # Initialize an array to hold the found files
    found_files = []

    # Check if the directory exists
    if Dir.exist?(base_dir)
      # Search for files
      Dir.glob("#{base_dir}/**/*").each do |file_path|
        if File.file?(file_path)
          # Check for content match
          if search_content && File.read(file_path).include?(search_content)
            found_files << file_path
          end

          # Check for filename match
          if search_filename && File.basename(file_path) == search_filename
            found_files << file_path unless found_files.include?(file_path)
          end
        end
      end
    end

    render json: { files: found_files }, status: :ok
  rescue => e
    render json: { error: e.message }, status: :bad_request
  end

  private

  def sanitize_search_dir(search_dir)
    # Remove any path traversal characters and ensure it is a valid directory name
    sanitized = search_dir.gsub(/(\.\.\/|\/)/, '')
    sanitized.empty? ? '' : sanitized
  end
end