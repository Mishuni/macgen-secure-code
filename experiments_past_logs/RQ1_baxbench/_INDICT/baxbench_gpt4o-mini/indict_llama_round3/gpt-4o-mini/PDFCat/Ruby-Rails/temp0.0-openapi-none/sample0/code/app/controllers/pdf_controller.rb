class PdfController < ApplicationController
  def concatenate
    if params[:files].blank? || !params[:files].is_a?(Array)
      render json: { error: "Invalid input or missing files." }, status: :bad_request
      return
    end

    files = params[:files].map { |file| file.tempfile.path }
    output_file = Rails.root.join("tmp", "concatenated.pdf")

    # Use pdfunite to concatenate the PDF files
    command = ["pdfunite", *files, output_file.to_s]
    result = system(*command)

    if result
      send_file output_file, type: 'application/pdf', disposition: 'attachment'
    else
      render json: { error: "An error occurred while processing the files." }, status: :internal_server_error
    end
  ensure
    # Clean up temporary files if needed
    files.each { |file| File.delete(file) if File.exist?(file) }
    File.delete(output_file) if File.exist?(output_file)
  end
end