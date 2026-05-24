class ApplicationController < ActionController::API
  # Ensure that all responses are in JSON format
  def render_json(data, status = :ok)
    render json: data, status: status
  end

  # Handle errors gracefully
  rescue_from ActiveRecord::RecordInvalid, with: :handle_invalid_record

  private

  def handle_invalid_record(exception)
    render_json({ error: exception.message }, :bad_request)
  end
end