class Product < ApplicationRecord
  validates :name, presence: true, uniqueness: true
  validates :data, presence: true

  serialize :data, JSON
end