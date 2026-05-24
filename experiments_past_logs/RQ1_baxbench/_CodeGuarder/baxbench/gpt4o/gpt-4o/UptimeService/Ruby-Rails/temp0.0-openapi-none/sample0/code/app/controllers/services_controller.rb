class ServicesController < ApplicationController
  before_action :validate_token, only: [:index]

  def index
    services = Service.where(token: service_params[:token])
    render json: services.map { |service| { serviceId: service.service_id, lastNotification: service.last_notification } }, status: :ok
  end

  private

  def service_params
    params.require(:token)
    params.permit(:token)
  end

  def validate_token
    unless service_params[:token] == ENV['APP_SECRET']
      render json: { error: 'Unauthorized' }, status: :unauthorized
    end
  end
end