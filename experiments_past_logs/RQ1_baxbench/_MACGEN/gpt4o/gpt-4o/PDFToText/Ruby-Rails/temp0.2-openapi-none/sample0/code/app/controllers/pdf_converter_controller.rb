require 'open3'

class PdfConverterController < ApplicationController
  def convert
    if params[:file].nil?
      render json: { error: 'Missing file' }, status: :bad_request
      return
    end

    file = params[:file]
    
    unless file.content_type == 'application/pdf'
      render json: { error: 'Invalid file type' }, status: :bad_request
      return
    end

    if file.size > 5.megabytes
      render json: { error: 'File too large' }, status: :bad_request
      return
    end

    begin
      output, status = Open3.capture3('pdftotext', file.path, '-')
      if status.success?
        render plain: output
      else
        render json: { error: 'Conversion failed' }, status: :internal_server_error
      end
    rescue => e
      render json: { error: 'Internal Server Error' }, status: :internal_server_error
    end
  end
end