class Product < ApplicationRecord
  serialize :tags, Array
  validates :product_name, presence: true
  validates :tags, presence: true
end