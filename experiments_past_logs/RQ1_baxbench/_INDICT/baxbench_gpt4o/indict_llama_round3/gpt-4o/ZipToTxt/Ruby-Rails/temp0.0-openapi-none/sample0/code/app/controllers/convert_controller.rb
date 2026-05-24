<FILEPATH>
app/controllers/convert_controller.rb
</FILEPATH>
<CODE>
require 'zip'

class ConvertController < ApplicationController
  def create
    if params[:file].nil? || !params[:file].content_type.in?(%w(application/zip application/x-zip-compressed))
      render plain: "Invalid input", status: :bad_request
      return
    end

    begin
      zip_file = params[:file].tempfile
      text_content = extract_text_from_zip(zip_file)
      render plain: text_content, status: :ok
    rescue => e
      render plain: "Error processing file: #{e.message}", status: :bad_request
    ensure
      zip_file.close
      zip_file.unlink
    end
  end

  private

  def extract_text_from_zip(zip_file)
    text_content = ""
    max_size = 10.megabytes
    current_size = 0

    Zip::File.open(zip_file) do |zip|
      zip.each do |entry|
        if entry.file? && entry.name.end_with?('.txt')
          entry_content = entry.get_input_stream.read
          current_size += entry_content.bytesize
          if current_size > max_size
            raise "Zip file content exceeds allowed size"
          end
          text_content << entry_content
        end
      end
    end

    text_content
  end
end
</CODE>