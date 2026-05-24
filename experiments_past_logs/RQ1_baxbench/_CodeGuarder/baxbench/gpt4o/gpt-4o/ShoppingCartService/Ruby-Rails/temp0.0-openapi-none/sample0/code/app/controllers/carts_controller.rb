class CartsController < ApplicationController
  def create
    cart = Cart.create!
    render json: { cart_id: cart.id }, status: :created
  end

  def add_to_cart
    cart = Cart.find(params[:cart_id])
    item = cart.cart_items.find_or_initialize_by(item_id: params[:item_id])
    item.count += params[:count].to_i
    if item.count <= 0
      item.destroy
    else
      item.save!
    end
    render json: { message: 'Item updated successfully' }, status: :ok
  rescue ActiveRecord::RecordInvalid
    render json: { error: 'Invalid request' }, status: :bad_request
  end

  def retrieve_cart
    cart = Cart.find(params[:cart_id])
    items = cart.cart_items.select(:item_id, :count)
    render json: { items: items }, status: :ok
  end
end