class CartsController < ApplicationController
  def create
    cart = Cart.create
    render_json({ cart_id: cart.id }, :created)
  end

  def add
    cart = Cart.find_by(id: params[:cart_id])
    return render_json({ error: 'Cart not found' }, :not_found) unless cart

    item_id = params[:item_id]
    count = params[:count]

    if count < 0
      cart.items.delete(item_id)
    else
      cart.items[item_id] = (cart.items[item_id] || 0) + count
    end

    cart.save
    render_json({ message: 'Item added or removed successfully' })
  end

  def retrieve
    cart = Cart.find_by(id: params[:cart_id])
    return render_json({ error: 'Cart not found' }, :not_found) unless cart

    items = cart.items.map { |item_id, count| { item_id: item_id, count: count } }
    render_json({ items: items })
  end
end