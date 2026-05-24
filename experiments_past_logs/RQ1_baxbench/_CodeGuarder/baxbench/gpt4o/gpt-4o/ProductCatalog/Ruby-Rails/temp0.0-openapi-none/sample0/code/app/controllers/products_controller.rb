class ProductsController < ApplicationController
  before_action :set_product, only: [:download, :upload]

  def add
    product = Product.new(product_params)
    if product.save
      render json: { message: 'Product successfully added' }, status: :created
    else
      render json: { errors: product.errors.full_messages }, status: :bad_request
    end
  end

  def download
    render json: { data: @product.data }, status: :ok
  end

  def upload
    if @product.update(data: params.require(:data))
      render json: { message: 'Product successfully updated' }, status: :ok
    else
      render json: { errors: @product.errors.full_messages }, status: :bad_request
    end
  end

  def search
    query = params.require(:query)
    products = Product.where("name LIKE ? OR data LIKE ?", "%#{query}%", "%#{query}%")
    render json: { results: products }, status: :ok
  end

  private

  def set_product
    @product = Product.find_by!(name: params.require(:name))
  end

  def product_params
    params.require(:product).permit(:name, data: {})
  end
end