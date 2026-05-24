class ServicesController < ApplicationController
  def create
    services = Service.where(token: params[:token])
    if services.empty?
      render json: { message: 'No services found for the provided token.' }, status: :not_found
    else
      render json: services.select(:service_id, :last_notification), status: :ok
    end
  rescue StandardError => e
    render json: { error: e.message }, status: :internal_server_error
  end
end