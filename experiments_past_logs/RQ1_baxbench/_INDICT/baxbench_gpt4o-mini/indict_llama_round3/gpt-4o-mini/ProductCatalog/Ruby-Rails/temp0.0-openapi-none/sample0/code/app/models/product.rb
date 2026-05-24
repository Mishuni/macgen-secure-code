class Product < ApplicationRecord
  validates :name, presence: true
  serialize :data, JSON
end