class Product < ApplicationRecord
  validates :product_name, presence: true
  validates :tags, presence: true
  serialize :tags, Array
end