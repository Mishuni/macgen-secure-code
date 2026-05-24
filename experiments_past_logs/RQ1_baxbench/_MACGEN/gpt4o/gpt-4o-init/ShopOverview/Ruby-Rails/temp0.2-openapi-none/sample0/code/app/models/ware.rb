class Ware < ApplicationRecord
  belongs_to :merchant

  validates :name, :description, :price, presence: true
end