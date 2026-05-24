class HeartbeatsController < ApplicationController
  def create
    service = Service.find_or_initialize_by(service_id: params[:serviceId])
    service.token = params[:token]
    service.last_notification = Time.current

    if service.save
      render json: { message: 'Heartbeat registered successfully.' }, status: :ok
    else
      render json: { error: 'Invalid request payload.' }, status: :bad_request
    end
  rescue StandardError => e
    render json: { error: e.message }, status: :internal_server_error
  end
end