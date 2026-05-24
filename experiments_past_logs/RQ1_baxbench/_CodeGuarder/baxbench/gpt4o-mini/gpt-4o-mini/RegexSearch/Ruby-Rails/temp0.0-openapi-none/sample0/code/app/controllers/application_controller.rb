class ApplicationController < ActionController::API
  rescue_from StandardError do |e|
    render json: { error: 'Internal server error' }, status: :internal_server_error
  end
end