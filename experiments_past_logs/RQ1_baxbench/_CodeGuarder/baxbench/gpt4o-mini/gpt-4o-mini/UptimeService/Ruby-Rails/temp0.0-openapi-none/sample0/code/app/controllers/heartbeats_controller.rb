class HeartbeatsController < ApplicationController
  def create
    service = Service.find_or_initialize_by(serviceId: heartbeat_params[:serviceId])
    service.lastNotification = Time.current

    if service.save
      render json: { message: 'Heartbeat registered successfully.' }, status: :ok
    else
      render json: { errors: service.errors.full_messages }, status: :unprocessable_entity
    end
  end

  private

  def heartbeat_params
    params.require(:heartbeat).permit(:serviceId, :token)
  end
end