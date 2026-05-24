class ApplicationController < ActionController::API
  rescue_from ActiveRecord::RecordNotFound, with: :record_not_found
  rescue_from ActiveRecord::RecordInvalid, with: :record_invalid

  private

  def record_not_found
    render json: { message: 'Record not found' }, status: :not_found
  end

  def record_invalid(exception)
    render json: { message: exception.record.errors.full_messages.join(', ') }, status: :unprocessable_entity
  end
end