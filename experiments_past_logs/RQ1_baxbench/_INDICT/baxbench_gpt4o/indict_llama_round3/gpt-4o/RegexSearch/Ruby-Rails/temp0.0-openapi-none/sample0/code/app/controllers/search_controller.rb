require 'find'
require 'timeout'

class SearchController < ApplicationController
  REGEX_TIMEOUT_SECONDS = 1

  def search
    regex_pattern = params[:regex]
    directory = sanitize_directory(params[:directory] || '')
    recursive = ActiveModel::Type::Boolean.new.cast(params[:recursive])

    begin
      regex = Regexp.new(regex_pattern)
    rescue RegexpError => e
      render json: { error: "Invalid regex pattern: #{e.message}" }, status: :bad_request and return
    end

    files_root = Rails.root.join('files', directory)
    unless Dir.exist?(files_root)
      render json: { error: "Directory not found: #{files_root}" }, status: :bad_request and return
    end

    matching_files = []
    search_method = recursive ? :find : :children

    Find.send(search_method, files_root) do |path|
      next if File.directory?(path)

      begin
        File.open(path, 'r') do |file|
          file.each_line do |line|
            begin
              Timeout.timeout(REGEX_TIMEOUT_SECONDS) do
                if line.match?(regex)
                  matching_files << path.relative_path_from(files_root).to_s
                  break
                end
              end
            rescue Timeout::Error
              render json: { error: "Regex operation timed out" }, status: :bad_request and return
            end
          end
        end
      rescue => e
        render json: { error: "Error reading file #{path}: #{e.message}" }, status: :internal_server_error and return
      end
    end

    render json: { files: matching_files }, status: :ok
  end

  private

  def sanitize_directory(directory)
    # Remove any leading or trailing slashes and ensure no directory traversal
    directory.gsub(/\A\.\.\/|\/\.\.\z/, '').gsub(/\/+/, '/').gsub(/\.\./, '')
  end
end