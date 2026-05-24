class ApplicationController < ActionController::API
  # Ensure all responses are JSON
  def render_json(data, status = :ok)
    render json: data, status: status
  end
end