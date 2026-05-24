class PdfConverterController < ApplicationController
  require 'tempfile'
  require 'shellwords'

  def convert
    file = params[:file]
    validate_file(file)

    Tempfile.create(['uploaded', '.pdf'], '/tmp') do |temp_file|
      temp_file.binmode
      temp_file.write(file.read)
      temp_file.rewind

      safe_file_path = Shellwords.escape(temp_file.path)
      converted_text = `pdftotext #{safe_file_path} -`
      render plain: converted_text, status: :ok
    end
  end

  private

  def validate_file(file)
    raise 'Invalid file type' unless file.content_type == 'application/pdf'
  end
end