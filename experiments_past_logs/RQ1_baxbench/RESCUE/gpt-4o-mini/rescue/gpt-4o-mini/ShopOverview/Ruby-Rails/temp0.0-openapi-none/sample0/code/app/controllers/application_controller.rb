class ApplicationController < ActionController::API
  # Ensure all responses are JSON
  def render_json(data, status = :ok)
    render json: data, status: status
  end

  # Handle errors and sanitize inputs
  def sanitize_input(input)
    ActionController::Base.helpers.sanitize(input)
  end
end