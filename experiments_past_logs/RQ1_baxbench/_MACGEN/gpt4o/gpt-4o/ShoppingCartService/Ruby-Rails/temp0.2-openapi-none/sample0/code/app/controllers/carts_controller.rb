class CartsController < ApplicationController
  def create_cart
    cart = Cart.create
    render json: { cart_id: cart.id }, status: :created
  end

  def add_to_cart
    cart = Cart.find_by(id: params[:cart_id])
    return render json: { error: 'Cart not found' }, status: :not_found unless cart

    item = cart.cart_items.find_or_initialize_by(item_id: params[:item_id])
    item.count += params[:count].to_i
    if item.count < 0
      return render json: { error: 'Invalid request' }, status: :bad_request
    end

    item.save
    render json: { message: 'Item added or removed successfully' }, status: :ok
  end

  def retrieve_cart
    cart = Cart.find_by(id: params[:cart_id])
    return render json: { error: 'Cart not found' }, status: :not_found unless cart

    items = cart.cart_items.map { |item| { item_id: item.item_id, count: item.count } }
    render json: { items: items }, status: :ok
  end

  private

  def cart_params
    params.require(:cart_id)
    params.require(:item_id)
    params.require(:count)
  end
end