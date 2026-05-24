class Product < ApplicationRecord
  validates :name, presence: true, uniqueness: true
  validates :additional_properties, presence: true

  serialize :additional_properties, JSON
end