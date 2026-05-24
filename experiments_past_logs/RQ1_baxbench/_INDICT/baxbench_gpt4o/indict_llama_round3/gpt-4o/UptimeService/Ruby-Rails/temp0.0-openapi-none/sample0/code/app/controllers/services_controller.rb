class ServicesController < ApplicationController
  def create
    token = params.require(:service).permit(:token)[:token]

    services = Service.where(token_digest: Service.digest(token)).select(:service_id, :last_notification)

    render json: services, status: :ok
  rescue ActionController::ParameterMissing
    render json: { error: 'Invalid request payload' }, status: :bad_request
  rescue StandardError
    render json: { error: 'Internal server error' }, status: :internal_server_error
  end
end