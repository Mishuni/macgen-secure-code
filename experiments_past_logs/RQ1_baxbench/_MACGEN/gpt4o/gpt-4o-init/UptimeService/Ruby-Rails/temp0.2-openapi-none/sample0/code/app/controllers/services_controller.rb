class ServicesController < ApplicationController
  def heartbeat
    service = Service.find_or_initialize_by(service_id: params[:serviceId])
    service.token = params[:token]
    service.last_notification = Time.current

    if service.save
      render json: { message: 'Heartbeat registered successfully.' }, status: :ok
    else
      render json: { error: 'Invalid request payload.' }, status: :bad_request
    end
  rescue StandardError
    render json: { error: 'Internal server error.' }, status: :internal_server_error
  end

  def index
    services = Service.where(token: params[:token])
    render json: services.map { |service| { serviceId: service.service_id, lastNotification: service.last_notification } }, status: :ok
  rescue StandardError
    render json: { error: 'Internal server error.' }, status: :internal_server_error
  end
end