class CompilationController < ApplicationController
  def compile
    file_name = params[:fileName]
    file_content = params[:fileContent]

    if file_name.nil? || file_content.nil?
      render json: { hasError: true, compilerError: "Invalid input" }, status: :bad_request
      return
    end

    result = compile_code(file_name, file_content)
    render json: result
  end

  private

  def compile_code(file_name, file_content)
    extension = File.extname(file_name)
    case extension
    when ".ts"
      compile_typescript(file_content)
    when ".cpp"
      compile_cpp(file_content)
    else
      { hasError: true, compilerError: "Unsupported file type" }
    end
  end

  def compile_typescript(content)
    Tempfile.create(['program', '.ts']) do |file|
      file.write(content)
      file.flush
      output = `tsc #{file.path} 2>&1`
      has_error = !$?.success?
      { hasError: has_error, compilerError: has_error ? output : nil }
    end
  end

  def compile_cpp(content)
    Tempfile.create(['program', '.cpp']) do |file|
      file.write(content)
      file.flush
      output = `g++ #{file.path} -o #{file.path}.out 2>&1`
      has_error = !$?.success?
      { hasError: has_error, compilerError: has_error ? output : nil }
    end
  end
end