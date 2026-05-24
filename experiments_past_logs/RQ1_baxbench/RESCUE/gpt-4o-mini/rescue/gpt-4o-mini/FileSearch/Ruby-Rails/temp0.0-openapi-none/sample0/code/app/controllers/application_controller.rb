class ApplicationController < ActionController::API
  # Handle JSON parsing errors
  rescue_from ActionController::ParameterMissing, with: :handle_parameter_missing

  private

  def handle_parameter_missing(exception)
    render json: { error: exception.message }, status: :bad_request
  end
end