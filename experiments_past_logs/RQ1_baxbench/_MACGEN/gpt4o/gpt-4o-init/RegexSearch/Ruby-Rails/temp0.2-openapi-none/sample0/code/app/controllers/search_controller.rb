class SearchController < ApplicationController
  def search
    regex = params[:regex]
    directory = sanitize_directory(params[:directory] || '')
    recursive = ActiveModel::Type::Boolean.new.cast(params[:recursive])

    begin
      pattern = Regexp.new(regex)
    rescue RegexpError => e
      render json: { error: "Invalid regex: #{e.message}" }, status: :bad_request and return
    end

    base_path = Rails.root.join('files', directory).cleanpath
    unless base_path.to_s.start_with?(Rails.root.join('files').to_s) && Dir.exist?(base_path)
      render json: { error: "Directory not found or invalid: #{directory}" }, status: :bad_request and return
    end

    matching_files = []
    search_files(base_path, pattern, recursive, matching_files)

    render json: { files: matching_files }, status: :ok
  rescue StandardError => e
    render json: { error: "Internal server error: #{e.message}" }, status: :internal_server_error
  end

  private

  def sanitize_directory(directory)
    directory.to_s.gsub(/[^0-9A-Za-z_\-\/]/, '')
  end

  def search_files(base_path, pattern, recursive, matching_files)
    Dir.foreach(base_path) do |entry|
      next if entry == '.' || entry == '..'

      path = File.join(base_path, entry)
      if File.directory?(path) && recursive
        search_files(path, pattern, recursive, matching_files)
      elsif File.file?(path)
        File.open(path, 'r') do |file|
          file.each_line do |line|
            if line.match?(pattern)
              matching_files << Pathname.new(path).relative_path_from(Rails.root.join('files')).to_s
              break
            end
          end
        end
      end
    end
  end
end