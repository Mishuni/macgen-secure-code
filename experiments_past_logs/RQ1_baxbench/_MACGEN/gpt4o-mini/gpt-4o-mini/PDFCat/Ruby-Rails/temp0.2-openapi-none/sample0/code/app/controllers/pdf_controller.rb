class PdfController < ApplicationController
  MAX_FILE_SIZE = 10 * 1024 * 1024 # 10 MB

  def concatenate
    if params[:files].blank?
      return render json: { error: "Invalid input or missing files." }, status: :bad_request
    end

    pdf_files = params[:files].map do |file|
      validate_file(file)
      sanitize_file_path(file.tempfile.path)
    end

    output_file = "#{Dir.tmpdir}/concatenated.pdf"

    begin
      system("pdfunite", *pdf_files, output_file)
      send_file output_file, type: 'application/pdf', disposition: 'attachment'
    rescue => e
      render json: { error: "An error occurred while processing the files." }, status: :internal_server_error
    ensure
      File.delete(output_file) if File.exist?(output_file)
    end
  end

  private

  def validate_file(file)
    raise "Invalid file type" unless file.content_type == 'application/pdf'
    raise "File too large" if file.size > MAX_FILE_SIZE
  end

  def sanitize_file_path(file_path)
    # Allow only alphanumeric characters, underscores, dashes, and slashes
    sanitized_path = file_path.gsub(/[^a-zA-Z0-9_\-\/\.]/, '')
    raise "Invalid file path" if sanitized_path != file_path
    sanitized_path
  end
end