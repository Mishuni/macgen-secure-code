class HeartbeatsController < ApplicationController
  before_action :validate_token, only: [:create]

  def create
    service = Service.find_or_initialize_by(service_id: heartbeat_params[:serviceId])
    service.update!(last_notification: Time.current)
    render json: { message: 'Heartbeat registered successfully.' }, status: :ok
  rescue ActiveRecord::RecordInvalid
    render json: { error: 'Invalid request payload.' }, status: :bad_request
  end

  private

  def heartbeat_params
    params.require(:serviceId)
    params.require(:token)
    params.permit(:serviceId, :token)
  end

  def validate_token
    unless heartbeat_params[:token] == ENV['APP_SECRET']
      render json: { error: 'Unauthorized' }, status: :unauthorized
    end
  end
end