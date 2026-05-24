class ServicesController < ApplicationController
  def register_heartbeat
    request_body = JSON.parse(request.body.read)
    service_id = request_body['serviceId']
    token = request_body['token']

    Service.register_heartbeat(service_id, token)
    render json: { message: 'Heartbeat registered successfully.' }, status: :ok
  rescue ActiveRecord::RecordInvalid
    render json: { error: 'Invalid request payload.' }, status: :bad_request
  end

  def get_services
    request_body = JSON.parse(request.body.read)
    token = request_body['token']

    services = Service.get_services(token)
    render json: services, status: :ok
  rescue ActiveRecord::RecordNotFound
    render json: { error: 'No services found.' }, status: :not_found
  end
end