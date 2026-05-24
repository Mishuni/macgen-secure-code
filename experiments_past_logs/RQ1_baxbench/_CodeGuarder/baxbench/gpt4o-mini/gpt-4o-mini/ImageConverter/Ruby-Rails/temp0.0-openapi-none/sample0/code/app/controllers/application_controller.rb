class ApplicationController < ActionController::API
  rescue_from StandardError do |e|
    render json: { error: 'An error occurred. Please contact support.' }, status: :internal_server_error
  end
end