class RecommenderController < ApplicationController
  def index
    tags = params[:tags].split(',').map(&:strip)
    products = Product.where('tags LIKE ?', "%#{tags.join('%')}%")
    render html: products.map { |p| "<a href='#'>#{ERB::Util.html_escape(p.product_name)}</a>" }.join('<br>').html_safe
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