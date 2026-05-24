require 'shellwords'

class ApplicationController < ActionController::API
  def concatenate
    if params[:files].nil? || !params[:files].is_a?(Array) || params[:files].empty?
      render json: { error: "Invalid input or missing files." }, status: :bad_request
      return
    end

    begin
      file_paths = params[:files].map do |file|
        path = Rails.root.join('tmp', file.original_filename)
        File.open(path, 'wb', 0600) { |f| f.write(file.read) }
        path
      end

      output_path = Rails.root.join('tmp', 'concatenated.pdf')
      system("pdfunite #{file_paths.map { |path| Shellwords.escape(path) }.join(' ')} #{Shellwords.escape(output_path)}")

      send_file output_path, type: 'application/pdf', disposition: 'inline'
    rescue => e
      render json: { error: "An error occurred while processing the files." }, status: :internal_server_error
    ensure
      file_paths.each { |path| File.delete(path) if File.exist?(path) }
      File.delete(output_path) if File.exist?(output_path)
    end
  end
end