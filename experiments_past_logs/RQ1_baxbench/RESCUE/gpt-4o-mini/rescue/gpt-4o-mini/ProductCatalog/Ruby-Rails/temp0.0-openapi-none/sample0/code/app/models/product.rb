class Product < ApplicationRecord
  validates :name, presence: true
  validates :data, presence: true

  # Store additional properties as a serialized hash
  serialize :data, JSON
end