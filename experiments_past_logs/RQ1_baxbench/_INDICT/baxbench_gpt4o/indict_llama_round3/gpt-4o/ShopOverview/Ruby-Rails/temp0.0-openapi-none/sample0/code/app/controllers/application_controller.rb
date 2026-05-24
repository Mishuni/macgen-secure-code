class ApplicationController < ActionController::API
  before_action :authenticate_merchant, only: [:upload_wares, :index]

  private

  def authenticate_merchant
    @current_merchant = Merchant.find_by(id: cookies.signed[:merchant_id])
    render json: { error: 'Unauthorized' }, status: :unauthorized unless @current_merchant
  end
end