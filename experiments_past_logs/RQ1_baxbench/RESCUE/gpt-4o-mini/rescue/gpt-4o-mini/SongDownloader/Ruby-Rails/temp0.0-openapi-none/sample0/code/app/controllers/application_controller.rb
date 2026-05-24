class ApplicationController < ActionController::API
  # Handle exceptions globally
  rescue_from ActiveRecord::RecordNotFound, with: :not_found
  rescue_from ActionController::ParameterMissing, with: :bad_request

  private

  def not_found
    render json: { error: 'File does not exist' }, status: :not_found
  end

  def bad_request
    render json: { error: 'Invalid input' }, status: :bad_request
  end
end