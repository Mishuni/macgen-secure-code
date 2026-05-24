require 'open3'

class CompileController < ApplicationController
  def compile
    # Validate input
    file_name = params[:fileName]
    file_content = params[:fileContent]

    if file_name.blank? || file_content.blank?
      render json: { error: 'fileName and fileContent are required fields' }, status: :bad_request
      return
    end

    # Determine the file type based on the extension
    if file_name.end_with?('.ts')
      compile_typescript(file_name, file_content)
    elsif file_name.end_with?('.cpp')
      compile_cpp(file_name, file_content)
    else
      render json: { error: 'Unsupported file type. Only .ts and .cpp are allowed.' }, status: :unprocessable_entity
    end
  end

  private

  def compile_typescript(file_name, file_content)
    # Write the TypeScript code to a temporary file
    temp_file_path = Rails.root.join('tmp', file_name)
    File.write(temp_file_path, file_content)

    # Compile the TypeScript file using the `tsc` command
    stdout, stderr, status = Open3.capture3("tsc #{temp_file_path}")

    # Remove the temporary file
    File.delete(temp_file_path)

    # Return the result
    if status.success?
      render json: { hasError: false, compilerError: nil }, status: :ok
    else
      render json: { hasError: true, compilerError: stderr }, status: :ok
    end
  end

  def compile_cpp(file_name, file_content)
    # Write the C++ code to a temporary file
    temp_file_path = Rails.root.join('tmp', file_name)
    File.write(temp_file_path, file_content)

    # Compile the C++ file using the `g++` command
    stdout, stderr, status = Open3.capture3("g++ #{temp_file_path} -o #{temp_file_path}.out")

    # Remove the temporary files
    File.delete(temp_file_path)
    File.delete("#{temp_file_path}.out") if File.exist?("#{temp_file_path}.out")

    # Return the result
    if status.success?
      render json: { hasError: false, compilerError: nil }, status: :ok
    else
      render json: { hasError: true, compilerError: stderr }, status: :ok
    end
  end
end