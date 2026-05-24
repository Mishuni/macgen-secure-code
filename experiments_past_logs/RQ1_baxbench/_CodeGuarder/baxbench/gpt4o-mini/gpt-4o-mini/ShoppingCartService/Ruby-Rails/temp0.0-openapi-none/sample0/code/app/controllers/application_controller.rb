class ApplicationController < ActionController::API
  # Handle JSON responses
  def render_json(data, status = :ok)
    render json: data, status: status
  end
end