class ApplicationController < ActionController::API
  # Handle JSON parsing errors
  rescue_from ActionController::ParameterMissing do |exception|
    render json: { error: exception.message }, status: :bad_request
  end

  # Handle ActiveRecord not found errors
  rescue_from ActiveRecord::RecordNotFound do |exception|
    render json: { error: 'Recipe not found' }, status: :not_found
  end
end