class CartItem < ApplicationRecord
  belongs_to :cart
  validates :item_id, presence: true
  validates :count, numericality: { only_integer: true }
end