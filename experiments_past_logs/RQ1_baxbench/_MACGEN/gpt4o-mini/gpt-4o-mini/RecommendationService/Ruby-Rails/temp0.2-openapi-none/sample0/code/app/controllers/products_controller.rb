class ProductsController < ApplicationController
  def recommender
    tags = params[:tags].gsub(/[^a-zA-Z0-9,]/, '').split(',').map(&:strip)
    products = Product.where("tags && ?", tags).pluck(:product_name, :tags)
    render html: products.map { |name, tags| "<div>#{h(name)} - Tags: #{h(tags.join(', '))}</div>" }.join.html_safe
  end

  def create
    product = Product.new(product_params)
    if product.save
      render json: { message: 'Product created successfully' }, status: :ok
    else
      render json: { error: 'Invalid input' }, status: :bad_request
    end
  end

  private

  def product_params
    params.require(:product).permit(:product_name, tags: [])
  end
end