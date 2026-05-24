class ApplicationController < ActionController::API
  # Error handling for JSON responses
  rescue_from StandardError do |e|
    render json: { error: e.message }, status: :internal_server_error
  end
end