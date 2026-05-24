class PdfsController < ApplicationController
  def convert
    if params[:file].blank?
      render json: { error: 'No file provided' }, status: :bad_request
      return
    end

    uploaded_file = params[:file]
    file_path = Rails.root.join('tmp', uploaded_file.original_filename)

    # Save the uploaded file temporarily
    File.open(file_path, 'wb') do |file|
      file.write(uploaded_file.read)
    end

    begin
      # Use pdftotext to convert PDF to text
      text = `pdftotext #{file_path} -`
      render plain: text, status: :ok
    rescue => e
      render json: { error: 'Conversion failed: ' + e.message }, status: :internal_server_error
    ensure
      # Clean up the temporary file
      File.delete(file_path) if File.exist?(file_path)
    end
  end
end