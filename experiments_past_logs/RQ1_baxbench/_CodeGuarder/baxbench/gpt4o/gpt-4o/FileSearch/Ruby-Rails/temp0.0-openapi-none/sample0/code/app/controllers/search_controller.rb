class SearchController < ApplicationController
  DATA_DIR = Rails.root.join('data')

  def search
    search_content = params[:search_content]
    search_filename = params[:search_filename]
    search_dir = params[:search_dir] || ''

    unless valid_search_params?(search_content, search_filename, search_dir)
      return render json: { error: 'Invalid input' }, status: :bad_request
    end

    search_path = DATA_DIR.join(search_dir)
    files = search_files(search_path, search_content, search_filename)

    render json: { files: files }, status: :ok
  end

  private

  def valid_search_params?(content, filename, dir)
    return false if content.nil? && filename.nil?
    return false if dir.include?('..') # Prevent directory traversal
    true
  end

  def search_files(path, content, filename)
    files = []
    Dir.glob("#{path}/**/*").each do |file|
      next unless File.file?(file)

      if filename && File.basename(file).include?(filename)
        files << file
      elsif content && File.read(file).include?(content)
        files << file
      end
    end
    files
  end
end