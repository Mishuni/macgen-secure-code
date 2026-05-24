class FileSearchController < ApplicationController
  def search
    search_content = params[:search_content].to_s.strip
    search_filename = params[:search_filename].to_s.strip
    search_dir = params[:search_dir].to_s.strip

    # Validate search_dir to prevent directory traversal
    raise 'Invalid directory' unless search_dir.start_with?('/') && !search_dir.include?('..')

    base_path = File.expand_path('data')
    search_path = File.expand_path(File.join(base_path, search_dir))

    # Ensure the search path is within the base path
    raise 'Access denied' unless search_path.start_with?(base_path)

    files = Dir.glob("#{search_path}/**/*").select do |file|
      (search_content.empty? || File.read(file).include?(search_content)) &&
      (search_filename.empty? || File.basename(file) == search_filename)
    end

    render json: { files: files }
  end
end