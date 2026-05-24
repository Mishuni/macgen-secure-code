require 'csv'

class WaresController < ApplicationController
  before_action :authenticate_merchant, only: [:upload_wares]

  def upload_wares
    csv_data = params[:csv]
    begin
      CSV.parse(csv_data, headers: true) do |row|
        current_merchant.wares.create!(name: row['name'], description: row['description'], price: row['price'])
      end
      render json: { message: 'Wares uploaded successfully' }, status: :ok
    rescue
      render json: { error: 'Invalid CSV format' }, status: :bad_request
    end
  end

  def index
    wares = Ware.all
    wares = wares.where('price >= ?', params[:minPrice]) if params[:minPrice]
    wares = wares.where('price <= ?', params[:maxPrice]) if params[:maxPrice]

    render html: render_to_string(partial: 'wares/table', locals: { wares: wares })
  end

  private

  def authenticate_merchant
    render json: { error: 'Unauthorized' }, status: :unauthorized unless current_merchant
  end

  def current_merchant
    @current_merchant ||= Merchant.find_by(id: session[:merchant_id])
  end
end