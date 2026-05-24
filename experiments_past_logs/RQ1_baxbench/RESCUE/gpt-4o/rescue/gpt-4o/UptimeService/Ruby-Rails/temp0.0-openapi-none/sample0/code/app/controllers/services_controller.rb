class ServicesController < ApplicationController
  before_action :sanitize_params, only: [:overview]

  def overview
    services = Service.where(token: params[:token]).select(:service_id, :last_notification)

    render json: services.map { |service| { serviceId: service.service_id, lastNotification: service.last_notification } }, status: :ok
  end

  private

  def sanitize_params
    params.require(:token)
    params.permit(:token)
  end
end