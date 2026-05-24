class PdfController < ApplicationController
  ALLOWED_CONTENT_TYPES = ['application/pdf'].freeze

  def convert
    if params[:file].present? && valid_pdf?(params[:file])
      file = params[:file].tempfile.path
      text = extract_text_from_pdf(file)
      render plain: text, content_type: 'text/plain'
    else
      render json: { error: 'Invalid input or missing file' }, status: :bad_request
    end
  end

  private

  def valid_pdf?(file)
    ALLOWED_CONTENT_TYPES.include?(file.content_type) && file.size > 0
  end

  def extract_text_from_pdf(file_path)
    output = `pdftotext #{Shellwords.escape(file_path)} -`
    raise 'Conversion failed' if $?.exitstatus != 0
    output
  end
end