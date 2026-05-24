class WaresController < ApplicationController
  def index
    wares = Ware.all
    wares = wares.where("price >= ?", params[:minPrice]) if params[:minPrice].present?
    wares = wares.where("price <= ?", params[:maxPrice]) if params[:maxPrice].present?

    render html: render_to_string(partial: "wares_table", locals: { wares: wares })
  end
end