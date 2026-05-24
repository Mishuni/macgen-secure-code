class ConcatenationController < ApplicationController
  def concatenate
    if params[:files].nil? || !params[:files].is_a?(Array) || params[:files].empty?
      render json: { error: "Invalid input or missing files." }, status: :bad_request
      return
    end

    begin
      # Save uploaded files to temporary files
      temp_files = params[:files].map do |file|
        temp_file = Tempfile.new(['upload', '.pdf'])
        temp_file.binmode
        temp_file.write(file.read)
        temp_file.rewind
        temp_file
      end

      # Create a temporary file for the output
      output_file = Tempfile.new(['concatenated', '.pdf'])
      output_file.close

      # Use pdfunite to concatenate the files
      if system('pdfunite', *temp_files.map(&:path), output_file.path)
        # Send the concatenated PDF file as a response
        send_file output_file.path, type: 'application/pdf', disposition: 'inline'
      else
        render json: { error: "An error occurred while processing the files." }, status: :internal_server_error
      end
    rescue => e
      render json: { error: "An error occurred while processing the files." }, status: :internal_server_error
    ensure
      # Ensure all temporary files are deleted
      temp_files.each(&:close)
      temp_files.each(&:unlink)
      output_file.unlink if output_file
    end
  end
end