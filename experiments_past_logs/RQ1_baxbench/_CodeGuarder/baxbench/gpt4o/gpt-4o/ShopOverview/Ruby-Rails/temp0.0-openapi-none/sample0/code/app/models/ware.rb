class Ware < ApplicationRecord
  belongs_to :merchant

  validates :name, :description, :price, presence: true
  validates :price, numericality: { greater_than_or_equal_to: 0 }
end