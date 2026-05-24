class ProductsController < ApplicationController
  def add
    product = Product.new(product_params)
    if product.save
      render json: { message: 'Product successfully added' }, status: :created
    else
      render json: { errors: product.errors.full_messages }, status: :bad_request
    end
  end

  def download
    product = Product.find_by(name: params[:name])
    if product
      render json: { data: product.properties }, status: :ok
    else
      render json: { error: 'Product not found' }, status: :not_found
    end
  end

  def upload
    product = Product.find_or_initialize_by(name: upload_params[:name])
    product.properties = upload_params[:data]
    if product.save
      render json: { message: 'Product updated successfully' }, status: :ok
    else
      render json: { errors: product.errors.full_messages }, status: :bad_request
    end
  end

  def search
    products = Product.where("name LIKE ? OR properties LIKE ?", "%#{params[:query]}%", "%#{params[:query]}%")
    render json: { results: products }, status: :ok
  end

  private

  def product_params
    params.require(:product).permit(:name, properties: {})
  end

  def upload_params
    params.require(:product).permit(:name, :data)
  end
end