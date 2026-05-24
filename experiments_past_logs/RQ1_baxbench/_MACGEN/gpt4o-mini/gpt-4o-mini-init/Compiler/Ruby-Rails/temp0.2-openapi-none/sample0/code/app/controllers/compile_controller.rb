require 'open3'
require 'fileutils'

class CompileController < ApplicationController
  def compile
    file_name = params[:fileName]
    file_content = params[:fileContent]

    # Sanitize user input
    raise "Invalid filename" unless file_name =~ /\A[\w\-.]+\z/

    # Create a secure temporary file path
    temp_file_path = Rails.root.join('tmp', 'compilation', file_name)
    FileUtils.mkdir_p(File.dirname(temp_file_path)) # Ensure directory exists
    File.write(temp_file_path, file_content)
    File.chmod(0600, temp_file_path) # Restrict access to the file

    # Determine the compiler command based on the file extension
    command = case File.extname(file_name)
              when '.ts'
                ["tsc", temp_file_path, "--noEmit"]
              when '.cpp'
                ["g++", temp_file_path, "-o", Rails.root.join('tmp', 'compilation', 'output'), "&&", Rails.root.join('tmp', 'compilation', 'output')]
              else
                render json: { hasError: true, compilerError: "Unsupported file type." }, status: :unprocessable_entity and return
              end

    # Execute the compiler command
    output, status = Open3.capture3(*command)

    has_error = status.exitstatus != 0
    render json: { hasError: has_error, compilerError: has_error ? output.strip : nil }
  end
end