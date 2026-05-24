class SearchController < ApplicationController
  DATA_DIRECTORY = Rails.root.join('data')

  def search
    search_content = params[:search_content]
    search_filename = params[:search_filename]
    search_dir = params[:search_dir] || ''

    # Ensure at least one search criterion is provided
    if search_content.nil? && search_filename.nil?
      render json: { error: 'At least one search criterion must be provided' }, status: :bad_request and return
    end

    # Validate search_dir to prevent directory traversal
    if search_dir.include?("..")
      render json: { error: 'Invalid directory' }, status: :bad_request and return
    end

    search_path = DATA_DIRECTORY.join(search_dir)

    unless Dir.exist?(search_path)
      render json: { error: 'Invalid directory' }, status: :bad_request and return
    end

    files = Dir.glob("#{search_path}/**/*").select do |file|
      File.file?(file) && (
        (search_filename && File.basename(file).include?(search_filename)) ||
        (search_content && File.read(file).include?(search_content))
      )
    end

    render json: { files: files }, status: :ok
  rescue => e
    render json: { error: e.message }, status: :bad_request
  end
end