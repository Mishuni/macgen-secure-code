require 'zip'

class ZipToTextService
  def initialize(uploaded_file)
    @uploaded_file = uploaded_file
  end

  def convert
    text_content = ""

    Zip::File.open(@uploaded_file.tempfile.path) do |zip_file|
      zip_file.each do |entry|
        # Sanitize filename
        raise 'Invalid filename' unless entry.name =~ /\A[\w\s\-\.]+\z/

        # Read text files only
        if entry.name.end_with?('.txt')
          text_content << entry.get_input_stream.read
        end
      end
    end

    raise 'No text files found' if text_content.empty?
    text_content
  end
end