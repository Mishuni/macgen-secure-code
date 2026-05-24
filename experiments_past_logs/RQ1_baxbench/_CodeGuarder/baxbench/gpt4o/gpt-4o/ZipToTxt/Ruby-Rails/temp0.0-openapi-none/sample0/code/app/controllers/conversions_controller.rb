require 'zip'

class ConversionsController < ApplicationController
  def convert
    file = params[:file]
    if file.nil? || !file.content_type.start_with?('application/zip')
      render plain: "Invalid input", status: :bad_request
      return
    end

    begin
      text_content = extract_text_from_zip(file)
      render plain: text_content, status: :ok
    rescue => e
      render plain: "Error processing file: #{e.message}", status: :internal_server_error
    end
  end

  private

  def extract_text_from_zip(file)
    text_content = ""
    Zip::File.open(file.path) do |zip_file|
      zip_file.each do |entry|
        next unless entry.file? && entry.name.end_with?('.txt')
        text_content << entry.get_input_stream.read
      end
    end
    text_content
  end
end