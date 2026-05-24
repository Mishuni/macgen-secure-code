class ApplicationController < ActionController::API
  rescue_from ActiveRecord::RecordInvalid, with: :render_bad_request
  rescue_from ActiveRecord::RecordNotFound, with: :render_not_found

  private

  def render_bad_request(exception)
    render json: { error: exception.message }, status: :bad_request
  end

  def render_not_found(exception)
    render json: { error: exception.message }, status: :not_found
  end
end