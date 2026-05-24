class ApplicationController < ActionController::API
  def convert
    if params[:file].nil?
      render json: { error: 'Missing file' }, status: :bad_request
      return
    end

    begin
      # Save the uploaded file to a temporary location
      uploaded_file = params[:file]
      temp_file_path = Rails.root.join('tmp', uploaded_file.original_filename)
      File.open(temp_file_path, 'wb') do |file|
        file.write(uploaded_file.read)
      end

      # Use pdftotext to convert PDF to text
      output = `pdftotext #{Shellwords.escape(temp_file_path.to_s)} -`
      if $?.success?
        render plain: output, status: :ok
      else
        render json: { error: 'Conversion failed' }, status: :internal_server_error
      end
    rescue => e
      render json: { error: e.message }, status: :internal_server_error
    ensure
      # Ensure the temporary file is deleted
      File.delete(temp_file_path) if File.exist?(temp_file_path)
    end
  end
end