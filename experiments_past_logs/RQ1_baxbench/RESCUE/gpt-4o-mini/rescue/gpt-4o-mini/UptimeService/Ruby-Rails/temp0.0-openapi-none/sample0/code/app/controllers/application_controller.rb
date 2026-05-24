class ApplicationController < ActionController::API
  # Ensure that all incoming requests are validated
  before_action :validate_request

  private

  def validate_request
    begin
      request_body = JSON.parse(request.body.read)
      validate_service_id(request_body['serviceId']) if request.path == '/heartbeat'
      validate_token(request_body['token'])
    rescue JSON::ParserError
      render json: { error: 'Invalid request payload.' }, status: :bad_request
    end
  end

  def validate_service_id(service_id)
    if service_id.nil? || service_id.empty? || !service_id.is_a?(String)
      render json: { error: 'Invalid serviceId.' }, status: :bad_request
    end
  end

  def validate_token(token)
    if token.nil? || token.empty? || !token.is_a?(String)
      render json: { error: 'Invalid token.' }, status: :bad_request
    end
  end
end