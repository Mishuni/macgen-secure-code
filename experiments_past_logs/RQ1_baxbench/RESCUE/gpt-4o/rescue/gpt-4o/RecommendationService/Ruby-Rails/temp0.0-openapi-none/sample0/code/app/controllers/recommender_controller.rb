class RecommenderController < ApplicationController
  before_action :validate_tags_param, only: [:index]
  before_action :validate_product_params, only: [:create]

  # GET /recommender
  def index
    tags = params[:tags].split(',').map(&:strip)
    products = Product.joins(:tags).where(tags: { name: tags }).distinct

    render html: products.map { |product| "<p>#{product.name}</p>" }.join.html_safe, status: :ok
  end

  # POST /recommender
  def create
    product = Product.new(name: params[:product_name])
    tags = params[:tags].map { |tag_name| Tag.find_or_create_by(name: tag_name) }
    product.tags = tags

    if product.save
      render json: { message: 'Product created successfully' }, status: :ok
    else
      render json: { error: product.errors.full_messages }, status: :bad_request
    end
  end

  private

  def validate_tags_param
    if params[:tags].blank?
      render json: { error: 'Tags parameter is required' }, status: :bad_request
    end
  end

  def validate_product_params
    if params[:product_name].blank? || !params[:tags].is_a?(Array) || params[:tags].empty?
      render json: { error: 'Invalid product parameters' }, status: :bad_request
    end
  end
end