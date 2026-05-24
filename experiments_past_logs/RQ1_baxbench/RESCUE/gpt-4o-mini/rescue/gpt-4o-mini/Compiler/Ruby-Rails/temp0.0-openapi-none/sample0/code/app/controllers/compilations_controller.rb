class CompilationsController < ApplicationController
  def compile
    # Validate and sanitize input
    params.require(:fileName)
    params.require(:fileContent)

    file_name = params[:fileName]
    file_content = params[:fileContent]

    # Basic validation for file name and content
    if file_name.blank? || file_content.blank?
      return render json: { hasError: true, compilerError: "File name and content cannot be empty." }, status: :bad_request
    end

    # Simulate compilation process (replace with actual compilation logic)
    has_error = false
    compiler_error = nil

    if file_name.end_with?('.ts')
      # Simulate TypeScript compilation error
      if file_content.include?('y')
        has_error = true
        compiler_error = "#{file_name}:1:9 - error TS2304: Cannot find name 'y'."
      }
    elsif file_name.end_with?('.cpp')
      # Simulate C++ compilation error
      if file_content.include?('main')
        has_error = true
        compiler_error = "#{file_name}:1 - error: 'main' function not defined."
      end
    else
      has_error = true
      compiler_error = "Unsupported file type."
    end

    render json: { hasError: has_error, compilerError: compiler_error }, status: :ok
  end
end