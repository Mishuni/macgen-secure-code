class ApplicationController < ActionController::API
  include ActionController::Cookies

  def authenticate_merchant!
    unless cookies.signed[:merchant_id]
      render json: { error: 'Unauthorized' }, status: :unauthorized
    end
  end
end