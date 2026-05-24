class SearchController < ApplicationController
  require 'json'
  require 'pathname'

  FILES_ROOT = Pathname.new('./files').realpath

  def search_files
    regex = params[:regex]
    directory = params[:directory] || ''
    recursive = ActiveModel::Type::Boolean.new.cast(params[:recursive])

    if regex.blank?
      render json: { error: 'Regex parameter is required' }, status: :bad_request and return
    end

    begin
      search_path = FILES_ROOT.join(directory).realpath
      raise 'Invalid directory path' unless search_path.start_with?(FILES_ROOT.to_s)

      files = []
      search_files_in_directory(search_path, regex, files, recursive)

      render json: { files: files }
    rescue => e
      render json: { error: e.message }, status: :bad_request
    end
  end

  private

  def search_files_in_directory(path, regex, files, recursive)
    Dir.foreach(path) do |entry|
      next if entry == '.' || entry == '..'

      file_path = path.join(entry)
      if File.directory?(file_path)
        search_files_in_directory(file_path, regex, files, recursive) if recursive
      else
        if File.file?(file_path) && File.read(file_path) =~ /#{regex}/
          files << file_path.relative_path_from(FILES_ROOT).to_s
        end
      end
    end
  end
end