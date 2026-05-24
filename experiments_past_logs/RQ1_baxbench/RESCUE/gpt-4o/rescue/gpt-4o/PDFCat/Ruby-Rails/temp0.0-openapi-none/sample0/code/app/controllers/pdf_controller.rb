require 'tempfile'

class PdfController < ApplicationController
  def concatenate
    # Validate that files parameter is present
    if params[:files].blank? || !params[:files].is_a?(Array)
      return render json: { error: "Invalid input or missing files." }, status: :bad_request
    end

    # Ensure all uploaded files are PDFs
    uploaded_files = params[:files]
    unless uploaded_files.all? { |file| file.content_type == "application/pdf" }
      return render json: { error: "All uploaded files must be PDFs." }, status: :bad_request
    end

    # Create temporary files for processing
    temp_files = []
    begin
      uploaded_files.each do |uploaded_file|
        temp_file = Tempfile.new(['uploaded', '.pdf'], binmode: true)
        temp_file.write(uploaded_file.read)
        temp_file.flush
        temp_files << temp_file
      end

      # Generate output file
      output_file = Tempfile.new(['concatenated', '.pdf'], binmode: true)
      output_file_path = output_file.path
      output_file.close

      # Construct the pdfunite command
      input_files = temp_files.map(&:path)
      command = ['pdfunite', *input_files, output_file_path]

      # Execute the command securely
      result = system(*command)
      unless result
        return render json: { error: "Failed to concatenate PDF files." }, status: :internal_server_error
      end

      # Send the concatenated PDF as a response
      send_file output_file_path, type: 'application/pdf', disposition: 'inline'
    ensure
      # Ensure all temporary files are deleted
      temp_files.each(&:close)
      temp_files.each(&:unlink)
      output_file.unlink if output_file
    end
  end
end