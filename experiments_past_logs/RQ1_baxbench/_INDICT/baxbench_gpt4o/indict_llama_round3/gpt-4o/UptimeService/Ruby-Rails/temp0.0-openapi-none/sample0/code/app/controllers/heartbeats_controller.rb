class HeartbeatsController < ApplicationController
  def create
    service_params = params.require(:heartbeat).permit(:serviceId, :token)

    service = Service.find_or_initialize_by(service_id: service_params[:serviceId])
    if service.authenticate_token(service_params[:token])
      service.last_notification = Time.current

      if service.save
        render json: { message: 'Heartbeat registered successfully' }, status: :ok
      else
        render json: { error: 'Internal server error' }, status: :internal_server_error
      end
    else
      render json: { error: 'Unauthorized' }, status: :unauthorized
    end
  rescue ActionController::ParameterMissing
    render json: { error: 'Invalid request payload' }, status: :bad_request
  end
end