class CompilationController < ApplicationController
  def compile
    request_body = request.body.read
    begin
      data = JSON.parse(request_body)
      file_name = data['fileName']
      file_content = data['fileContent']

      if file_name.end_with?('.ts')
        result = compile_typescript(file_content)
      elsif file_name.end_with?('.cpp')
        result = compile_cpp(file_content)
      else
        render json: { hasError: true, compilerError: "Unsupported file type." }, status: :unprocessable_entity and return
      end

      render json: result
    rescue JSON::ParserError
      render json: { hasError: true, compilerError: "Invalid JSON format." }, status: :unprocessable_entity
    end
  end

  private

  def compile_typescript(content)
    # Simulate TypeScript compilation
    # In a real application, you would call the TypeScript compiler here
    if content.include?('y')
      { hasError: true, compilerError: "TypeScript compilation error: Cannot find name 'y'." }
    else
      { hasError: false, compilerError: nil }
    end
  end

  def compile_cpp(content)
    # Simulate C++ compilation
    # In a real application, you would call the C++ compiler here
    if content.include?('main')
      { hasError: false, compilerError: nil }
    else
      { hasError: true, compilerError: "C++ compilation error: Missing main function." }
    end
  end
end