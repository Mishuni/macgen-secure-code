class ApplicationController < ActionController::API
  # Handle JSON responses and error handling
  rescue_from StandardError do |e|
    render json: { error: e.message }, status: :bad_request
  end
end