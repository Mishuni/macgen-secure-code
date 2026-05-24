class Product < ApplicationRecord
  validates :product_name, presence: true
  validates :tags, presence: true
end