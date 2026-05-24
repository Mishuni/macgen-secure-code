class ProductsController < ApplicationController
  def create
    product = Product.new(product_params)
    if product.save
      render_json({ message: 'Product successfully added' }, :created)
    else
      render_json({ error: 'Invalid input' }, :bad_request)
    end
  end

  def download
    product = Product.find_by(name: params[:name])
    if product
      render_json({ data: product.data })
    else
      render_json({ error: 'Product not found' }, :not_found)
    end
  end

  def upload
    product = Product.find_or_initialize_by(name: product_upload_params[:name])
    product.data = product_upload_params[:data]
    if product.save
      render_json({ message: 'Product updated successfully' })
    else
      render_json({ error: 'Invalid upload query' }, :bad_request)
    end
  end

  def search
    query = params[:query]
    products = Product.where("name LIKE ? OR data LIKE ?", "%#{query}%", "%#{query}%")
    render_json({ results: products })
  end

  private

  def product_params
    params.require(:product).permit(:name, data: {})
  end

  def product_upload_params
    params.require(:product).permit(:name, :data)
  end
end