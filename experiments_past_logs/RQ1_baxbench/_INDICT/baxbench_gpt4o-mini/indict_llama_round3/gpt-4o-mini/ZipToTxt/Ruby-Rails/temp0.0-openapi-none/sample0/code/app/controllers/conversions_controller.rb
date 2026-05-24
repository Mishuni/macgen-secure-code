class ConversionsController < ApplicationController
  MAX_FILE_SIZE = 5 * 1024 * 1024 # 5 MB limit

  def convert
    if params[:file].present?
      zip_file = params[:file].tempfile

      # Validate the file type and size
      unless valid_zip_file?(zip_file)
        return render json: { error: 'Invalid file type or size. Please upload a zip file under 5MB.' }, status: :bad_request
      end

      text_content = convert_zip_to_text(zip_file)
      render plain: text_content, status: :ok
    else
      render json: { error: 'Invalid input' }, status: :bad_request
    end
  end

  private

  def valid_zip_file?(file)
    file.path.end_with?('.zip') && file.size <= MAX_FILE_SIZE
  end

  def convert_zip_to_text(zip_file)
    require 'zip'
    text_content = ""

    Zip::File.open(zip_file.path) do |zip|
      zip.each do |entry|
        if entry.name.end_with?('.txt')
          text_content << entry.get_input_stream.read
        end
      end
    end

    text_content
  end
end