class SearchController < ApplicationController
  require 'json'
  require 'pathname'

  def index
    regex = params[:regex]
    directory = params[:directory] || ''
    recursive = params[:recursive] == 'true'

    if regex.blank?
      render json: { error: 'Regex parameter is required.' }, status: :bad_request and return
    end

    unless valid_directory?(directory)
      render json: { error: 'Invalid directory path.' }, status: :bad_request and return
    end

    begin
      files = search_files(regex, directory, recursive)
      render json: { files: files }, status: :ok
    rescue RegexpError => e
      render json: { error: "Invalid regex: #{e.message}" }, status: :bad_request
    rescue => e
      render json: { error: "Internal server error: #{e.message}" }, status: :internal_server_error
    end
  end

  private

  def valid_directory?(directory)
    # Ensure the directory is a valid path and does not traverse outside the base directory
    base_path = Rails.root.join('files')
    target_path = base_path.join(directory).expand_path
    target_path.start_with?(base_path.to_s) && Dir.exist?(target_path)
  end

  def search_files(regex, directory, recursive)
    root_path = Rails.root.join('files', directory)
    files = []

    if recursive
      Dir.glob("#{root_path}/**/*").each do |file|
        if File.file?(file) && File.read(file).match?(Regexp.new(regex))
          files << Pathname.new(file).relative_path_from(Pathname.new(root_path)).to_s
        end
      end
    else
      Dir.glob("#{root_path}/*").each do |file|
        if File.file?(file) && File.read(file).match?(Regexp.new(regex))
          files << Pathname.new(file).relative_path_from(Pathname.new(root_path)).to_s
        end
      end
    end

    files
  end
end