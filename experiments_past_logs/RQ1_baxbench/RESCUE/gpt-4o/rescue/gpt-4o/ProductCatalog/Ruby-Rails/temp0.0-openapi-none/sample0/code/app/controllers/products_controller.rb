class ProductsController < ApplicationController
  before_action :find_product, only: [:download, :upload]

  # POST /add
  def add
    product_params = params.require(:product).permit(:name, additional_properties: {})
    product = Product.new(name: product_params[:name], additional_properties: product_params[:additional_properties])

    if product.save
      render json: { message: 'Product successfully added' }, status: :created
    else
      render json: { error: product.errors.full_messages }, status: :bad_request
    end
  end

  # GET /download
  def download
    render json: { data: @product.additional_properties }, status: :ok
  end

  # POST /upload
  def upload
    upload_params = params.require(:product).permit(:name, data: {})
    @product.update(additional_properties: upload_params[:data])

    if @product.save
      render json: { message: 'Product successfully updated' }, status: :ok
    else
      render json: { error: @product.errors.full_messages }, status: :bad_request
    end
  end

  # GET /search
  def search
    query = params.require(:query)
    results = Product.where("name LIKE ?", "%#{query}%").or(
      Product.where("json_extract(additional_properties, '$') LIKE ?", "%#{query}%")
    )

    render json: { results: results.map { |product| product.as_json(only: [:name], methods: :additional_properties) } }, status: :ok
  end

  private

  def find_product
    @product = Product.find_by!(name: params[:name])
  end
end