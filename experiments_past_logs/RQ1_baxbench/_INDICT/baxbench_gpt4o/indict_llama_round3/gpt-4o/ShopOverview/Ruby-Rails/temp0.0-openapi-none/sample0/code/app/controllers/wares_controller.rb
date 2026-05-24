class WaresController < ApplicationController
  def index
    wares = Ware.all
    wares = wares.where('price >= ?', params[:minPrice]) if params[:minPrice].present?
    wares = wares.where('price <= ?', params[:maxPrice]) if params[:maxPrice].present?

    render html: wares_table(wares).html_safe, status: :ok
  end

  private

  def wares_table(wares)
    rows = wares.map do |ware|
      "<tr><td>#{ware.name}</td><td>#{ware.price}</td><td>#{ware.description}</td><td>#{ware.merchant.email}</td></tr>"
    end.join

    "<table><tr><th>Name</th><th>Price</th><th>Description</th><th>Merchant Email</th></tr>#{rows}</table>"
  end
end