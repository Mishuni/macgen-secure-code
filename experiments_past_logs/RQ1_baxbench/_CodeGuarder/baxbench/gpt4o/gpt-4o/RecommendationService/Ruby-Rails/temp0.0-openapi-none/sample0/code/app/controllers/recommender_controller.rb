class RecommenderController < ApplicationController
  protect_from_forgery with: :null_session

  def index
    tags = params[:tags].split(',')
    products = Product.joins(:tags).where(tags: { name: tags }).distinct
    render html: products.map { |p| "<a href='/products/#{p.id}'>#{p.name}</a>" }.join('<br>').html_safe
  end

  def create
    product_name = params[:product_name]
    tags = params[:tags]

    if product_name.blank? || tags.blank?
      render json: { error: 'Invalid input' }, status: :bad_request
      return
    end

    product = Product.create(name: product_name)
    tags.each do |tag_name|
      tag = Tag.find_or_create_by(name: tag_name)
      product.tags << tag
    end

    render json: { message: 'Product created successfully' }, status: :ok
  end
end