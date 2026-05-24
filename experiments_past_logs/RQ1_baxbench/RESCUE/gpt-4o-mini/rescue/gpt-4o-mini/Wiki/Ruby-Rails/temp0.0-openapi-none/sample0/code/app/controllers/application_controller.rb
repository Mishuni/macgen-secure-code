class ApplicationController < ActionController::API
  # Ensure all responses are JSON
  def render_json(data, status = :ok)
    render json: data, status: status
  end

  # Handle not found responses
  def not_found
    render json: { error: 'Not Found' }, status: :not_found
  end
end