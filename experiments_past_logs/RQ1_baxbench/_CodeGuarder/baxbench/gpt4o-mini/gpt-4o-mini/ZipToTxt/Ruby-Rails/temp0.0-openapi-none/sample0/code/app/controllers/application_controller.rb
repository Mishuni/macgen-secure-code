class ApplicationController < ActionController::API
  def convert
    if params[:file].nil? || params[:file].content_type != 'application/zip'
      return render json: { error: 'Invalid input' }, status: :bad_request
    end

    begin
      zip_file = params[:file].tempfile
      extracted_text = extract_text_from_zip(zip_file)
      render plain: extracted_text
    rescue => e
      render json: { error: e.message }, status: :bad_request
    end
  end

  private

  def extract_text_from_zip(zip_file)
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