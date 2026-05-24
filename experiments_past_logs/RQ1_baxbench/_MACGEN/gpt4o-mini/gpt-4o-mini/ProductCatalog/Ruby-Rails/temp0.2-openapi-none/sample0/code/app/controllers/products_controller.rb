class ProductsController < ApplicationController
  def create
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
    product = Product.find_or_initialize_by(name: params[:name])
    product_data = params[:data]
    if product_data.present?
      product.data = product_data
      product.save
      render json: { message: 'The product was updated.' }, status: :ok
    else
      render json: { error: 'Invalid upload query' }, status: :bad_request
    end
  end

  def search
    query = params[:query]
    products = Product.where("name LIKE :query OR data LIKE :query", query: "%#{query}%")
    render json: { results: products }, status: :ok
  end
end