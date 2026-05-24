class CartsController < ApplicationController
  def create_cart
    cart = Cart.create!
    render json: { cart_id: cart.id }, status: :created
  end

  def add_to_cart
    sanitized_cart_id = params[:cart_id].to_s.strip
    item_id = params[:item_id].to_i
    count = params[:count].to_i

    raise ArgumentError, 'Invalid cart_id' if sanitized_cart_id.empty?
    raise ArgumentError, 'Count must be an integer' unless count.is_a?(Integer)

    cart = Cart.find_by(id: sanitized_cart_id)
    return render json: { error: 'Cart not found' }, status: :not_found unless cart

    item = cart.cart_items.find_or_initialize_by(item_id: item_id)
    item.count = [item.count.to_i + count, 0].max
    item.save!

    render json: { message: 'Item added or removed successfully' }, status: :ok
  rescue ArgumentError => e
    render json: { error: e.message }, status: :bad_request
  end

  def retrieve_cart
    sanitized_cart_id = params[:cart_id].to_s.strip

    raise ArgumentError, 'Invalid cart_id' if sanitized_cart_id.empty?

    cart = Cart.find_by(id: sanitized_cart_id)
    return render json: { error: 'Cart not found' }, status: :not_found unless cart

    items = cart.cart_items.select(:item_id, :count)
    render json: { items: items }, status: :ok
  rescue ArgumentError => e
    render json: { error: e.message }, status: :bad_request
  end
end