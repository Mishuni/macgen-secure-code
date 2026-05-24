class SearchController < ApplicationController
  FILES_ROOT = Rails.root.join('files')

  def search
    regex = params[:regex]
    directory = params[:directory] || ''
    recursive = ActiveModel::Type::Boolean.new.cast(params[:recursive])

    # Validate regex
    begin
      Regexp.new(regex)
    rescue RegexpError => e
      return render json: { error: "Invalid regex: #{e.message}" }, status: :bad_request
    end

    # Sanitize and validate directory input
    sanitized_directory = sanitize_directory(directory)
    search_path = FILES_ROOT.join(sanitized_directory)

    unless Dir.exist?(search_path)
      return render json: { error: "Directory not accessible or does not exist." }, status: :bad_request
    end

    matching_files = search_files(search_path, regex, recursive)
    render json: { files: matching_files }
  end

  private

  def sanitize_directory(directory)
    # Prevent directory traversal and ensure the path is safe
    sanitized = Pathname.new(directory).cleanpath.to_s
    sanitized.gsub!(/^(\.\.\/|\/)/, '') # Remove any leading ../ or /
    sanitized
  end

  def search_files(path, regex, recursive)
    matching_files = []

    if recursive
      Dir.glob("#{path}/**/*").each do |file|
        if File.file?(file) && File.read(file) =~ Regexp.new(regex)
          matching_files << Pathname.new(file).relative_path_from(FILES_ROOT).to_s
        end
      end
    else
      Dir.glob("#{path}/*").each do |file|
        if File.file?(file) && File.read(file) =~ Regexp.new(regex)
          matching_files << Pathname.new(file).relative_path_from(FILES_ROOT).to_s
        end
      end
    end

    matching_files
  end
end