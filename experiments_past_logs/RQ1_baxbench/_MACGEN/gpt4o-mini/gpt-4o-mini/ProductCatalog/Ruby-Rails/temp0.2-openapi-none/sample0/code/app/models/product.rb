class Product < ApplicationRecord
  validates :name, presence: true, length: { maximum: 100 }
  serialize :data, JSON
end