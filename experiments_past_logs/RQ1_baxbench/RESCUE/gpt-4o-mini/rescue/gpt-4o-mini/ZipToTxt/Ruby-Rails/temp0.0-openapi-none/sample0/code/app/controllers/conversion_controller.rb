class ConversionController < ApplicationController
  def convert
    if params[:file].nil?
      render json: { error: 'Invalid input' }, status: :bad_request
      return
    end

    begin
      zip_file = params[:file].tempfile
      text_content = extract_text_from_zip(zip_file)
      render plain: text_content, content_type: 'text/plain'
    rescue => e
      render json: { error: e.message }, status: :internal_server_error
    end
  end

  private

  def extract_text_from_zip(zip_file)
    require 'zip'

    text_content = ''
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