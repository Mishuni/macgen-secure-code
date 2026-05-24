class ProductsController < ApplicationController
  before_action :set_product, only: [:download, :upload]

  def add
    product = Product.new(product_params)
    if product.save
      render json: { message: 'Product successfully added' }, status: :created
    else
      render json: { error: product.errors.full_messages.to_sentence }, status: :unprocessable_entity
    end
  end

  def download
    if @product
      render json: { data: @product.data }, status: :ok
    else
      render json: { error: 'Product not found' }, status: :not_found
    end
  end

  def upload
    if @product.update(data: sanitized_data)
      render json: { message: 'The product with the given name was updated.' }, status: :ok
    else
      render json: { error: @product.errors.full_messages.to_sentence }, status: :unprocessable_entity
    end
  end

  def search
    query = params[:query]
    if query.present?
      results = Product.where("name LIKE :query OR data LIKE :query", query: "%#{sanitize_sql_like(query)}%")
      render json: { results: results }, status: :ok
    else
      render json: { error: 'Invalid search query' }, status: :bad_request
    end
  end

  private

  def set_product
    @product = Product.find_by(name: params[:name])
  end

  def product_params
    params.require(:product).permit(:name, :data)
  end

  def sanitized_data
    # Implement any necessary sanitization logic here
    params[:data].to_s.strip
  end

  def sanitize_sql_like(string)
    ActiveRecord::Base.sanitize_sql_like(string)
  end
end