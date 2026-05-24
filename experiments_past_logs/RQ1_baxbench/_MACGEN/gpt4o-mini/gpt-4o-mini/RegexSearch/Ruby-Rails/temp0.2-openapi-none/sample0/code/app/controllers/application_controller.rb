class ApplicationController < ActionController::API
  ALLOWED_DIRECTORIES = ['subdir1', 'subdir2'] # Define allowed directories

  def search
    regex_pattern = params[:regex]
    directory = params[:directory] || ''
    recursive = params[:recursive] == 'true'

    # Validate regex length
    if regex_pattern.length > 100
      render json: { error: "Regex pattern too long" }, status: :bad_request and return
    end

    # Validate regex format
    begin
      Regexp.new(regex_pattern)
    rescue RegexpError => e
      render json: { error: "Invalid regex: #{e.message}" }, status: :bad_request and return
    end

    # Validate directory
    unless ALLOWED_DIRECTORIES.include?(directory)
      render json: { error: "Invalid directory" }, status: :bad_request and return
    end

    # Set the base directory
    base_directory = Rails.root.join('files', directory)

    # Check if the directory exists
    unless Dir.exist?(base_directory)
      render json: { error: "Directory not found: #{base_directory}" }, status: :bad_request and return
    end

    # Search for files
    files = []
    search_pattern = recursive ? '**/*' : '*'
    Dir.glob(base_directory.join(search_pattern)).each do |file_path|
      next unless File.file?(file_path)

      content = File.read(file_path)
      if content.match?(Regexp.new(regex_pattern))
        files << Pathname.new(file_path).relative_path_from(base_directory).to_s
      end
    end

    render json: { files: files }
  rescue => e
    render json: { error: "Internal server error: #{e.message}" }, status: :internal_server_error
  end
end