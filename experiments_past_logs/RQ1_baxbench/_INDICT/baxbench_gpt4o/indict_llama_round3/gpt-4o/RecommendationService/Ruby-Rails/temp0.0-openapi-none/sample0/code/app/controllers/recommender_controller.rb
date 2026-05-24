class RecommenderController < ApplicationController
  def index
    tags = params[:tags].to_s.split(',')
    products = Product.joins(:tags).where(tags: { name: tags }).distinct
    render html: products.map { |product| "<p>#{ERB::Util.html_escape(product.name)}</p>" }.join.html_safe
  end

  def create
    product = Product.new(name: product_params[:product_name])
    if product.save
      product_params[:tags].each do |tag_name|
        tag = Tag.find_or_create_by(name: tag_name)
        product.tags << tag
      end
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