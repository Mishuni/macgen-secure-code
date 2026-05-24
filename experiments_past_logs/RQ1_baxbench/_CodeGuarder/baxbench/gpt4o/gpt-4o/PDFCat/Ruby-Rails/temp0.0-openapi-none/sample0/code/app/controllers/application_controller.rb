class ApplicationController < ActionController::API
  def concatenate
    if params[:files].nil? || !params[:files].is_a?(Array) || params[:files].empty?
      render json: { error: "Invalid input or missing files." }, status: :bad_request
      return
    end

    begin
      # Create a temporary directory to store uploaded files
      Dir.mktmpdir do |dir|
        input_files = []

        # Save each uploaded file to the temporary directory
        params[:files].each_with_index do |file, index|
          file_path = File.join(dir, "file#{index}.pdf")
          File.open(file_path, 'wb') do |f|
            f.write(file.read)
          end
          input_files << file_path
        end

        # Define the output file path
        output_file_path = File.join(dir, "concatenated.pdf")

        # Use pdfunite to concatenate the PDF files
        system("pdfunite", *input_files, output_file_path)

        # Send the concatenated PDF file as a response
        send_file output_file_path, type: 'application/pdf', disposition: 'inline'
      end
    rescue => e
      render json: { error: "An error occurred while processing the files." }, status: :internal_server_error
    end
  end
end