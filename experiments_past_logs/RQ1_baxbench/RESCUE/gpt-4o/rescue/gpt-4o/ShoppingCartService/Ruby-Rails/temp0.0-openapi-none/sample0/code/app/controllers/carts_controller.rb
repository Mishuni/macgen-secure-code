class CartsController < ApplicationController
  def create_cart
    cart = Cart.create!
    render json: { cart_id: cart.id }, status: :created
  end

  def add_to_cart
    cart = Cart.find(params.require(:cart_id))
    item_id = params.require(:item_id)
    count = params.require(:count)

    cart_item = cart.cart_items.find_or_initialize_by(item_id: item_id)
    cart_item.count += count.to_i

    if cart_item.count <= 0
      cart_item.destroy
    else
      cart_item.save!
    end

    render json: { message: 'Item updated successfully' }, status: :ok
  end

  def retrieve_cart
    cart = Cart.find(params.require(:cart_id))
    items = cart.cart_items.select(:item_id, :count)

    render json: { items: items }, status: :ok
  end
end