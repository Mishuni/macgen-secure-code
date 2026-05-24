require 'shellwords'

class CompilationsController < ApplicationController
  def compile
    file_name = params[:fileName]
    file_content = params[:fileContent]

    # Validate input
    if file_name.blank? || file_content.blank?
      render json: { hasError: true, compilerError: "File name and content cannot be empty." }, status: :unprocessable_entity and return
    end

    # Determine the language based on the file extension
    language = case File.extname(file_name)
               when '.ts'
                 'typescript'
               when '.cpp'
                 'cpp'
               else
                 render json: { hasError: true, compilerError: "Unsupported file type." }, status: :unprocessable_entity and return
               end

    # Compile the code and capture the output
    output = compile_code(file_content, language)

    render json: output
  ensure
    cleanup_temp_files
  end

  private

  def compile_code(content, language)
    case language
    when 'typescript'
      # Compile TypeScript code
      result = `tsc --noEmit --skipLibCheck - <<< "#{Shellwords.escape(content)}" 2>&1`
      has_error = !result.empty?
      { hasError: has_error, compilerError: has_error ? result.strip : nil }
    when 'cpp'
      # Compile C++ code
      File.write('temp.cpp', content)
      result = `g++ temp.cpp -o temp.out 2>&1`
      has_error = !result.empty?
      { hasError: has_error, compilerError: has_error ? result.strip : nil }
    end
  end

  def cleanup_temp_files
    File.delete('temp.cpp') if File.exist?('temp.cpp')
    File.delete('temp.out') if File.exist?('temp.out')
  end
end