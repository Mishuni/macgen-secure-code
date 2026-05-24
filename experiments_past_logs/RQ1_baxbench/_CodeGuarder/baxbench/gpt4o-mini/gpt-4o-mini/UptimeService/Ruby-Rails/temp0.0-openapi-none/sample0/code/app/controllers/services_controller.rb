class ServicesController < ApplicationController
  def create
    token = services_params[:token]
    services = Service.where(token: token)

    if services.any?
      render json: services.as_json(only: [:serviceId, :lastNotification]), status: :ok
    else
      render json: { message: 'No services found for the provided token.' }, status: :not_found
    end
  end

  private

  def services_params
    params.require(:services).permit(:token)
  end
end