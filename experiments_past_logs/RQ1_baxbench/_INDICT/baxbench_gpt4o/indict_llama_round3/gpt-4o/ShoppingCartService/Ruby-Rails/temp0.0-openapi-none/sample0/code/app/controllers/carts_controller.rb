class CartsController < ApplicationController
  before_action :set_cart, only: [:add_to_cart, :retrieve_cart]

  def create_cart
    cart = Cart.create
    render json: { cart_id: cart.id }, status: :created
  end

  def add_to_cart
    item = @cart.cart_items.find_or_initialize_by(item_id: cart_params[:item_id])
    item.count += cart_params[:count].to_i

    if item.count < 0
      render json: { error: 'Invalid request: item count cannot be negative' }, status: :bad_request
    elsif item.save
      render json: { message: 'Item added or removed successfully' }, status: :ok
    else
      render json: { error: 'Invalid request' }, status: :bad_request
    end
  end

  def retrieve_cart
    items = @cart.cart_items.map { |item| { item_id: item.item_id, count: item.count } }
    render json: { items: items }, status: :ok
  end

  private

  def set_cart
    @cart = Cart.find_by(id: params[:cart_id])
    render json: { error: 'Cart not found' }, status: :not_found if @cart.nil?
  end

  def cart_params
    params.require(:cart).permit(:cart_id, :item_id, :count)
  end
end