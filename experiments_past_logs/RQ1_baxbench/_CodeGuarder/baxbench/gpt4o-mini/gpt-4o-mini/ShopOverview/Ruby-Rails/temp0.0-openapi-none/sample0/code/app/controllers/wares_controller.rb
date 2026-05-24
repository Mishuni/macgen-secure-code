class WaresController < ApplicationController
  before_action :authenticate_merchant!

  def upload
    csv_data = params[:csv]
    # CSV parsing logic here
    # Assuming CSV is parsed and wares are created
    render json: { message: 'Wares uploaded successfully' }, status: :ok
  end

  def index
    wares = Ware.all
    if params[:minPrice]
      wares = wares.where('price >= ?', params[:minPrice])
    end
    if params[:maxPrice]
      wares = wares.where('price <= ?', params[:maxPrice])
    end
    render json: wares, status: :ok
  end

  private

  def authenticate_merchant!
    unless cookies.signed[:AUTH_COOKIE]
      render json: { error: 'Unauthorized' }, status: :unauthorized
    end
  end
end