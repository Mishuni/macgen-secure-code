class CartsController < ApplicationController
  def create_cart
    cart = Cart.create!
    render json: { cart_id: cart.id }, status: :created
  end

  def add_to_cart
    cart = Cart.find_by(id: params[:cart_id])
    if cart.nil?
      render json: { error: 'Cart not found' }, status: :not_found
      return
    end

    item = cart.cart_items.find_or_initialize_by(item_id: params[:item_id])
    item.count += params[:count]
    item.save!

    render json: { message: 'Item added or removed successfully' }, status: :ok
  rescue ActiveRecord::RecordInvalid
    render json: { error: 'Invalid request' }, status: :bad_request
  end

  def retrieve_cart
    cart = Cart.find_by(id: params[:cart_id])
    if cart.nil?
      render json: { error: 'Cart not found' }, status: :not_found
      return
    end

    items = cart.cart_items.select(:item_id, :count)
    render json: { items: items }, status: :ok
  end
end