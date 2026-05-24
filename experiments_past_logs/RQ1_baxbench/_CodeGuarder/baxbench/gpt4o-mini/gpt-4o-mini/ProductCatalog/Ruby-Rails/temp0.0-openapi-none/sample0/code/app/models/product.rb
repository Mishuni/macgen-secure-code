class Product < ApplicationRecord
  validates :name, presence: true
  serialize :properties, JSON
end