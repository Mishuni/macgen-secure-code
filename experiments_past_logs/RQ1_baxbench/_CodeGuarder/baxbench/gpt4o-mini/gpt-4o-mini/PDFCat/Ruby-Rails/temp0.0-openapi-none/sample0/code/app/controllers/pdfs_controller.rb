class PdfsController < ApplicationController
  def concatenate
    if params[:files].blank?
      render json: { error: "Invalid input or missing files." }, status: :bad_request
      return
    end

    pdf_files = params[:files].map { |file| file.tempfile.path }
    output_file = Rails.root.join("tmp", "concatenated.pdf")

    begin
      # Use pdfunite to concatenate the PDF files
      system("pdfunite #{pdf_files.join(' ')} #{output_file}")

      if $?.success?
        send_file output_file, type: 'application/pdf', disposition: 'attachment'
      else
        render json: { error: "An error occurred while processing the files." }, status: :internal_server_error
      end
    ensure
      # Clean up the output file after sending
      File.delete(output_file) if File.exist?(output_file)
    end
  end
end