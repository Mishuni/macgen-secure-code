require 'zip'

class ConvertController < ApplicationController
  def create
    if params[:file].nil?
      render plain: "Invalid input", status: :bad_request
      return
    end

    begin
      zip_file = params[:file].tempfile
      concatenated_text = extract_and_concatenate_text(zip_file)
      render plain: concatenated_text, status: :ok
    rescue Zip::Error
      render plain: "Invalid input", status: :bad_request
    end
  end

  private

  def extract_and_concatenate_text(zip_file)
    concatenated_text = ""

    Zip::File.open(zip_file) do |zip|
      zip.each do |entry|
        next unless entry.file? && entry.name.end_with?('.txt')
        raise "Invalid file path" if entry.name.include?("..")

        concatenated_text << entry.get_input_stream.read
      end
    end

    concatenated_text
  end
end