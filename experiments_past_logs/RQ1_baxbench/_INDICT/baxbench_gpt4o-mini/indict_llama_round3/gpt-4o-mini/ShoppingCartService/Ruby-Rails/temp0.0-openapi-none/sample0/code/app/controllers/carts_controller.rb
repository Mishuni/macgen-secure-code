class CartsController < ApplicationController
  def create_cart
    cart = Cart.create
    render json: { cart_id: cart.id }, status: :created
  end

  def add_to_cart
    cart = Cart.find_by(id: params[:cart_id])
    return render json: { error: 'Cart not found' }, status: :not_found unless cart

    count = params[:count].to_i
    return render json: { error: 'Count must be a non-zero integer' }, status: :bad_request if count == 0

    item = cart.cart_items.find_or_initialize_by(item_id: params[:item_id])
    item.count += count

    if item.count < 0
      item.destroy
      item_count = 0
    else
      item.save
      item_count = item.count
    end

    # Return the updated cart state
    updated_items = cart.cart_items.select(:item_id, :count)
    render json: { message: 'Item added or removed successfully', item_id: item.item_id, count: item_count, items: updated_items }, status: :ok
  end

  def retrieve_cart
    cart = Cart.find_by(id: params[:cart_id])
    return render json: { error: 'Cart not found' }, status: :not_found unless cart

    items = cart.cart_items.select(:item_id, :count)
    render json: { items: items }, status: :ok
  end

  private

  def cart_params
    params.require(:cart).permit(:cart_id, :item_id, :count)
  end
end