class WaresController < ApplicationController
  def index
    @wares = Ware.all
    @wares = @wares.where('price >= ?', params[:minPrice]) if params[:minPrice].present?
    @wares = @wares.where('price <= ?', params[:maxPrice]) if params[:maxPrice].present?
    render json: @wares.includes(:merchant).as_json(include: { merchant: { only: :email } })
  end
end