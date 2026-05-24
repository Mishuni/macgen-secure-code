require 'yaml'
require 'fileutils'

class SearchController < ApplicationController
  FILES_ROOT = Rails.root.join('files').freeze

  def search
    regex = params.require(:regex)
    directory = params[:directory] || '.'
    recursive = ActiveModel::Type::Boolean.new.cast(params[:recursive])

    # Validate regex
    begin
      pattern = Regexp.new(regex)
    rescue RegexpError => e
      return render json: { error: "Invalid regex: #{e.message}" }, status: :bad_request
    end

    # Validate directory
    search_path = FILES_ROOT.join(directory).cleanpath
    unless search_path.to_s.start_with?(FILES_ROOT.to_s) && Dir.exist?(search_path)
      return render json: { error: "Invalid or inaccessible directory: #{directory}" }, status: :bad_request
    end

    # Search files
    files = []
    Dir.glob("#{search_path}/**/*", File::FNM_DOTMATCH) do |file|
      next if File.directory?(file)
      next unless recursive || File.dirname(file) == search_path.to_s

      begin
        File.open(file, 'r') do |f|
          files << file.sub("#{FILES_ROOT}/", '') if f.read.match?(pattern)
        end
      rescue Errno::EACCES
        # Skip files that cannot be read
        next
      end
    end

    render json: { files: files }, status: :ok
  end
end