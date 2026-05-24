class ApplicationController < ActionController::API
  # Ensure that all responses are in JSON format
  def render_json(data, status = :ok)
    render json: data, status: status
  end
end