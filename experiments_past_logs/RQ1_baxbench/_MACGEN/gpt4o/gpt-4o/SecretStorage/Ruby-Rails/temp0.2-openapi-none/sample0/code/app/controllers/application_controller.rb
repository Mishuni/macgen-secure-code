class ApplicationController < ActionController::API
  rescue_from ActiveRecord::RecordInvalid, with: :render_unprocessable_entity_response
  rescue_from ActiveRecord::RecordNotFound, with: :render_not_found_response

  private

  def render_unprocessable_entity_response(exception)
    render json: { message: exception.record.errors.full_messages.join(", ") }, status: :unprocessable_entity
  end

  def render_not_found_response(exception)
    render json: { message: exception.message }, status: :not_found
  end
end