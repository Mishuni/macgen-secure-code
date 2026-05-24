class RecommenderController < ApplicationController
  def index
    tags = params[:tags].split(',').map(&:strip).reject(&:empty?)
    products = Product.where("tags && ?", tags).distinct
    render html: products.map { |product| "<div>#{sanitize(product.product_name)} - Tags: #{sanitize(product.tags.join(', '))}</div>" }.join.html_safe
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