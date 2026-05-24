class WaresController < ApplicationController
  def index
    min_price = params[:minPrice].to_f
    max_price = params[:maxPrice].to_f

    # Logic to retrieve wares from the database goes here
    # For example: wares = Ware.where(price: min_price..max_price)

    # Render wares as an HTML table
    render json: { wares: [] } # Placeholder for actual wares data
  end
end