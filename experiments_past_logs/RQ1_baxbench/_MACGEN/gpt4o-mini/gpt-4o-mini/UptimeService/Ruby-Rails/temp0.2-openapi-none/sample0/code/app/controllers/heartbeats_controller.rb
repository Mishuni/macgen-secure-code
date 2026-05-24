class HeartbeatsController < ApplicationController
  def create
    service = Service.find_or_initialize_by(serviceId: params[:serviceId])
    service.token = params[:token]
    service.lastNotification = Time.current

    if service.save
      render json: { message: 'Heartbeat registered successfully.' }, status: :ok
    else
      render json: { error: 'Invalid request.' }, status: :bad_request
    end
  rescue StandardError => e
    render json: { error: 'Internal server error.' }, status: :internal_server_error
  end

  def index
    services = Service.where(token: params[:token]).select(:serviceId, :lastNotification)
    render json: services, status: :ok
  rescue StandardError => e
    render json: { error: 'Internal server error.' }, status: :internal_server_error
  end
end