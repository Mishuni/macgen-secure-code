class CartItem < ApplicationRecord
  belongs_to :cart
  validates :count, numericality: { greater_than_or_equal_to: 0 }
end