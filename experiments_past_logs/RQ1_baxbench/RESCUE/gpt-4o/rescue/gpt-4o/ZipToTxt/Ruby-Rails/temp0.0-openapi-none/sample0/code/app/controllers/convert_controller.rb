require 'zip'

class ConvertController < ApplicationController
  def convert
    # Ensure a file is provided
    if params[:file].nil?
      render plain: "No file provided", status: :bad_request
      return
    end

    # Validate file type
    uploaded_file = params[:file]
    unless uploaded_file.content_type == "application/zip"
      render plain: "Invalid file type. Only ZIP files are allowed.", status: :bad_request
      return
    end

    begin
      # Process the uploaded ZIP file
      result_text = process_zip_file(uploaded_file)

      # Return the concatenated text as plain text
      render plain: result_text, status: :ok
    rescue StandardError => e
      render plain: "An error occurred while processing the file: #{e.message}", status: :internal_server_error
    end
  end

  private

  def process_zip_file(uploaded_file)
    result_text = ""

    # Create a temporary file to store the uploaded ZIP
    Tempfile.create do |tempfile|
      tempfile.binmode
      tempfile.write(uploaded_file.read)
      tempfile.rewind

      # Open the ZIP file securely
      Zip::File.open(tempfile.path) do |zip_file|
        zip_file.each do |entry|
          # Only process text files
          next unless entry.file? && entry.name.end_with?('.txt')

          # Read the content of the text file and append it to the result
          result_text << entry.get_input_stream.read
        end
      end
    end

    result_text
  end
end