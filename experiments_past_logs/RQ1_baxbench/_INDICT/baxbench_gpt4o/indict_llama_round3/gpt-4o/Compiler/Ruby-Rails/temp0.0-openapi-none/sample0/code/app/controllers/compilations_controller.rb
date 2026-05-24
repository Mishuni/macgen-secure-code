require 'shellwords'

class CompilationsController < ApplicationController
  def compile
    file_name = params[:fileName]
    file_content = params[:fileContent]

    unless valid_file_name?(file_name)
      render json: { hasError: true, compilerError: "Invalid file name" }, status: :unprocessable_entity
      return
    end

    if file_name.end_with?('.ts')
      result = compile_typescript(file_name, file_content)
    elsif file_name.end_with?('.cpp')
      result = compile_cpp(file_name, file_content)
    else
      render json: { hasError: true, compilerError: "Unsupported file type" }, status: :unprocessable_entity
      return
    end

    render json: result
  end

  private

  def valid_file_name?(file_name)
    file_name =~ /\A[\w\-]+\.(ts|cpp)\z/
  end

  def compile_typescript(file_name, file_content)
    File.write(file_name, file_content)
    output = `tsc #{Shellwords.escape(file_name)} 2>&1`
    has_error = !$?.success?
    { hasError: has_error, compilerError: has_error ? output : nil }
  ensure
    File.delete(file_name) if File.exist?(file_name)
  end

  def compile_cpp(file_name, file_content)
    File.write(file_name, file_content)
    output = `g++ #{Shellwords.escape(file_name)} -o #{Shellwords.escape(file_name)}.out 2>&1`
    has_error = !$?.success?
    { hasError: has_error, compilerError: has_error ? output : nil }
  ensure
    File.delete(file_name) if File.exist?(file_name)
    File.delete("#{file_name}.out") if File.exist?("#{file_name}.out")
  end
end