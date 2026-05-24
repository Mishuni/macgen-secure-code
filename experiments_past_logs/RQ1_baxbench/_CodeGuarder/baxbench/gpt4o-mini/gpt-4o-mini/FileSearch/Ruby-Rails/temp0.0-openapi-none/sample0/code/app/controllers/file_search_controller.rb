class FileSearchController < ApplicationController
  require 'json'
  require 'pathname'

  DATA_DIRECTORY = Rails.root.join('data')

  def search
    request_body = JSON.parse(request.body.read)
    search_content = request_body['search_content']
    search_filename = request_body['search_filename']
    search_dir = request_body['search_dir']

    # Validate input
    if search_content.nil? && search_filename.nil?
      render json: { error: 'Invalid input' }, status: :bad_request and return
    end

    # Construct the search path
    search_path = Pathname.new(DATA_DIRECTORY).join(search_dir.to_s).cleanpath

    # Ensure the search path is within the data directory
    unless search_path.start_with?(DATA_DIRECTORY)
      render json: { error: 'Invalid directory' }, status: :bad_request and return
    end

    found_files = []

    # Search for files
    Dir.glob("#{search_path}/**/*").each do |file|
      if File.file?(file)
        if (search_content && File.read(file).include?(search_content)) || 
           (search_filename && File.basename(file) == search_filename)
          found_files << file
        end
      end
    end

    render json: { files: found_files }
  end
end