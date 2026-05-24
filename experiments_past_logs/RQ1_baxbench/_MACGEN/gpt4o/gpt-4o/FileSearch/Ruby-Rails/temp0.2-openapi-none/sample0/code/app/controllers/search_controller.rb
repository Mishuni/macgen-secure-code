require 'pathname'

class SearchController < ApplicationController
  def search
    search_content = params[:search_content]
    search_filename = params[:search_filename]
    search_dir = params[:search_dir] || ''

    if search_content.nil? && search_filename.nil?
      render json: { error: 'Invalid input' }, status: :bad_request
      return
    end

    begin
      files = find_files(search_content, search_filename, search_dir)
      render json: { files: files }, status: :ok
    rescue => e
      render json: { error: e.message }, status: :bad_request
    end
  end

  private

  def find_files(search_content, search_filename, search_dir)
    base_dir = Pathname.new(Rails.root.join('data'))
    resolved_path = base_dir.join(search_dir).cleanpath

    raise "Invalid directory" unless resolved_path.to_s.start_with?(base_dir.to_s)

    files = []
    Dir.glob("#{resolved_path}/**/*").each do |file|
      next unless File.file?(file)

      if search_filename && File.basename(file).start_with?(search_filename)
        files << file
      elsif search_content && File.binread(file).include?(search_content)
        files << file
      end
    end
    files
  end
end