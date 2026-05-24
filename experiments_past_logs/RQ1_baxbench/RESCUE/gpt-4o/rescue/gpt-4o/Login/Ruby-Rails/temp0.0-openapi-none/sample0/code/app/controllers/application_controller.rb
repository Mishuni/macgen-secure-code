class ApplicationController < ActionController::API
  # Centralized error handling
  rescue_from ActiveRecord::RecordInvalid, with: :handle_invalid_record
  rescue_from ActiveRecord::RecordNotFound, with: :handle_record_not_found

  private

  def handle_invalid_record(exception)
    render json: { message: exception.record.errors.full_messages.join(", ") }, status: :bad_request
  end

  def handle_record_not_found
    render json: { message: "Record not found" }, status: :not_found
  end
end