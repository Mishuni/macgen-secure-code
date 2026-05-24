class WaresController < ApplicationController
  def upload
    csv_data = params[:csv]
    begin
      CSV.parse(csv_data, headers: true) do |row|
        raise "Invalid data" unless valid_ware_data?(row)
        Ware.create!(row.to_h)
      end
      render json: { message: 'Wares uploaded successfully' }, status: :ok
    rescue CSV::MalformedCSVError
      render json: { error: 'Invalid CSV format' }, status: :unprocessable_entity
    rescue => e
      render json: { error: e.message }, status: :unprocessable_entity
    end
  end

  def index
    wares = Ware.all
    wares = wares.where('price >= ?', params[:minPrice]) if params[:minPrice]
    wares = wares.where('price <= ?', params[:maxPrice]) if params[:maxPrice]
    render json: wares
  end

  private

  def valid_ware_data?(row)
    row['name'].present? && row['description'].present? && row['price'].to_f > 0
  end
end