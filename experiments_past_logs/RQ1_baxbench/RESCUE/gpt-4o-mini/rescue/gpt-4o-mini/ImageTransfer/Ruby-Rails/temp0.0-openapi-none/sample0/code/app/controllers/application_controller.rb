class ApplicationController < ActionController::API
  # Handle exceptions globally
  rescue_from StandardError do |e|
    render json: { error: e.message }, status: :internal_server_error
  end
end