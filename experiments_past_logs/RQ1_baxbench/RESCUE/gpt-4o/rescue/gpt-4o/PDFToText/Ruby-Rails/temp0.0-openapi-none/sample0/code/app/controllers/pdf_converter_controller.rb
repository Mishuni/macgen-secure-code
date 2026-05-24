require 'open3'

class PdfConverterController < ApplicationController
  def convert
    # Validate the presence of the file parameter
    uploaded_file = params.require(:file)

    # Ensure the uploaded file is a PDF
    unless uploaded_file.content_type == 'application/pdf'
      render json: { error: 'Invalid file type. Only PDF files are allowed.' }, status: :bad_request
      return
    end

    # Save the uploaded file temporarily
    temp_file_path = Rails.root.join('tmp', "upload_#{SecureRandom.uuid}.pdf")
    File.open(temp_file_path, 'wb') do |file|
      file.write(uploaded_file.read)
    end

    # Extract text from the PDF using `pdftotext`
    begin
      output_text = extract_text_from_pdf(temp_file_path)
      render plain: output_text, content_type: 'text/plain'
    rescue => e
      Rails.logger.error("PDF conversion failed: #{e.message}")
      render json: { error: 'Failed to convert PDF to text.' }, status: :internal_server_error
    ensure
      # Ensure the temporary file is deleted
      File.delete(temp_file_path) if File.exist?(temp_file_path)
    end
  end

  private

  def extract_text_from_pdf(file_path)
    # Use Open3 to safely execute the `pdftotext` command
    stdout, stderr, status = Open3.capture3("pdftotext", "-layout", file_path, "-")
    raise "pdftotext error: #{stderr}" unless status.success?

    stdout
  end
end