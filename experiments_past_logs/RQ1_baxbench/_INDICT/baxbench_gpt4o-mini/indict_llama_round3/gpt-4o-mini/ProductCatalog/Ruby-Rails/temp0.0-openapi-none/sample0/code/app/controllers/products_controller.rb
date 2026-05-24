class ProductsController < ApplicationController
  before_action :set_product, only: [:upload]

  def add
    product = Product.new(product_params)
    if product.save
      render json: { message: 'Product successfully added' }, status: :created
    else
      render json: { error: 'Invalid input' }, status: :bad_request
    end
  end

  def download
    product = Product.find_by(name: params[:name])
    if product
      render json: { data: product.to_json }, status: :ok
    else
      render json: { error: 'Product not found' }, status: :not_found
    end
  end

  def upload
    if @product.update(product_params)
      render json: { message: 'The product was updated.' }, status: :ok
    else
      render json: { error: 'Invalid upload query' }, status: :bad_request
    end
  end

  def search
    products = Product.where("name LIKE ? OR data LIKE ?", "%#{params[:query]}%", "%#{params[:query]}%")
    render json: { results: products.as_json }, status: :ok
  end

  private

  def set_product
    @product = Product.find_by(name: params[:name])
    render json: { error: 'Product not found' }, status: :not_found unless @product
  end

  def product_params
    params.require(:product).permit(:name, data: {})
  end
end