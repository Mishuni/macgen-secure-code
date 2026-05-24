class PdfController < ApplicationController
  require 'tempfile'

  def concatenate
    files = params[:files]

    # Validate input
    if files.nil? || files.empty?
      return render json: { error: "Invalid input or missing files." }, status: :bad_request
    end

    # Create a temporary file for the concatenated PDF
    Tempfile.create(['concatenated', '.pdf']) do |output_file|
      # Prepare the command for pdfunite
      command = ['pdfunite']
      files.each do |file|
        # Sanitize file input to prevent directory traversal
        sanitized_file = sanitize_file_path(file)
        command << sanitized_file if sanitized_file
      end
      command << output_file.path

      # Execute the command
      system(*command)

      # Check if the command was successful
      if $?.success?
        # Send the concatenated PDF as a response
        send_file output_file.path, type: 'application/pdf', disposition: 'attachment'
      else
        render json: { error: "An error occurred while processing the files." }, status: :internal_server_error
      end
    end
  end

  private

  def sanitize_file_path(file)
    # Ensure the file path is valid and does not contain directory traversal characters
    if file =~ /\.\.\/|\/|\\/
      nil # Invalid file path
    else
      file # Valid file path
    end
  end
end