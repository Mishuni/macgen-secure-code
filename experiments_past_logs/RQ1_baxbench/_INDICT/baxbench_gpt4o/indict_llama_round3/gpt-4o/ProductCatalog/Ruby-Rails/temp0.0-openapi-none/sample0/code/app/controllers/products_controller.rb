class ProductsController < ApplicationController
  before_action :set_product, only: [:download, :upload]

  def add
    product = Product.new(product_params)
    if product.save
      render json: { message: 'Product successfully added' }, status: :created
    else
      render json: { error: 'Invalid input', details: product.errors.full_messages }, status: :bad_request
    end
  end

  def download
    if @product
      render json: { data: @product.data.to_json }, status: :ok
    else
      render json: { error: 'Product not found' }, status: :not_found
    end
  end

  def upload
    if @product.update(data: JSON.parse(params[:data]))
      render json: { message: 'The product with the given name was updated.' }, status: :ok
    else
      render json: { error: 'Invalid upload query', details: @product.errors.full_messages }, status: :bad_request
    end
  rescue JSON::ParserError
    render json: { error: 'Invalid JSON format' }, status: :bad_request
  end

  def search
    query = params[:query]
    if query.present?
      results = Product.where("name LIKE :query OR data LIKE :query", query: "%#{query}%")
      render json: { results: results.map(&:attributes) }, status: :ok
    else
      render json: { error: 'Invalid search query' }, status: :bad_request
    end
  end

  private

  def set_product
    @product = Product.find_by(name: params[:name])
  end

  def product_params
    params.permit(:name, data: {})
  end
end