require 'open3'
require 'tempfile'

class ApplicationController < ActionController::API
  def compile
    file_name = sanitize_file_name(params[:fileName])
    file_content = params[:fileContent]

    if file_name.nil? || file_content.nil?
      render json: { hasError: true, compilerError: 'Invalid input' }, status: :unprocessable_entity
      return
    end

    result = if file_name.end_with?('.ts')
               compile_typescript(file_content)
             elsif file_name.end_with?('.cpp')
               compile_cpp(file_content)
             else
               { hasError: true, compilerError: 'Unsupported file type' }
             end

    render json: result
  end

  private

  def sanitize_file_name(file_name)
    return nil unless file_name.is_a?(String)
    sanitized_name = file_name.gsub(/[^0-9A-Za-z.\-_]/, '')
    sanitized_name if sanitized_name.end_with?('.ts', '.cpp')
  end

  def compile_typescript(file_content)
    Tempfile.create(['source', '.ts']) do |file|
      file.write(file_content)
      file.flush
      stdout, stderr, status = Open3.capture3("tsc", file.path)
      { hasError: !status.success?, compilerError: stderr.presence }
    end
  end

  def compile_cpp(file_content)
    Tempfile.create(['source', '.cpp']) do |file|
      file.write(file_content)
      file.flush
      stdout, stderr, status = Open3.capture3("g++", file.path, "-o", "#{file.path}.out")
      { hasError: !status.success?, compilerError: stderr.presence }
    end
  end
end