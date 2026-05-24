class HeartbeatController < ApplicationController
  before_action :sanitize_params, only: [:register]

  def register
    service = Service.find_or_initialize_by(service_id: params[:serviceId], token: params[:token])
    service.last_notification = Time.current

    if service.save
      render json: { message: 'Heartbeat registered successfully' }, status: :ok
    else
      render json: { error: 'Failed to register heartbeat' }, status: :internal_server_error
    end
  end

  private

  def sanitize_params
    params.require(:serviceId)
    params.require(:token)
    params.permit(:serviceId, :token)
  end
end