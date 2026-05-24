class SearchController < ApplicationController
  DATA_DIR = Rails.root.join('data')

  def search
    search_content = params[:search_content]
    search_filename = params[:search_filename]
    search_dir = params[:search_dir]

    # Sanitize and validate inputs
    sanitized_dir = sanitize_directory(search_dir)
    files = find_files(sanitized_dir, search_content, search_filename)

    render json: { files: files }
  end

  private

  def sanitize_directory(dir)
    return '' if dir.blank?

    # Ensure the directory is safe and within the DATA_DIR
    sanitized = Pathname.new(dir).cleanpath.to_s
    raise ArgumentError, 'Invalid directory' unless sanitized.start_with?(DATA_DIR.to_s)

    sanitized
  end

  def find_files(search_dir, search_content, search_filename)
    files = []

    # Search for files in the specified directory
    Dir.glob("#{search_dir}/**/*").each do |file|
      if File.file?(file)
        if matches_content?(file, search_content) || matches_filename?(file, search_filename)
          files << file
        end
      end
    end

    files
  end

  def matches_content?(file, content)
    return false if content.blank?

    File.read(file).include?(content)
  rescue Errno::EACCES
    false
  end

  def matches_filename?(file, filename)
    return false if filename.blank?

    File.basename(file).start_with?(filename)
  end
end