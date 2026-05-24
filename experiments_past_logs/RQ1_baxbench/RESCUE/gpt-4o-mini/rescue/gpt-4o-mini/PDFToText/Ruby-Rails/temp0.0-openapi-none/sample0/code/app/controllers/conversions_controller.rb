class ConversionsController < ApplicationController
  def convert
    if params[:file].blank?
      render json: { error: 'Missing file' }, status: :bad_request
      return
    end

    begin
      # Save the uploaded file temporarily
      uploaded_file = params[:file]
      temp_file_path = Rails.root.join('tmp', uploaded_file.original_filename)
      File.open(temp_file_path, 'wb') do |file|
        file.write(uploaded_file.read)
      end

      # Use pdftotext to convert the PDF to text
      text_output = `pdftotext #{temp_file_path} -`
      File.delete(temp_file_path) # Clean up the temporary file

      render plain: text_output, content_type: 'text/plain'
    rescue => e
      render json: { error: 'Conversion failed: ' + e.message }, status: :internal_server_error
    end
  end
end