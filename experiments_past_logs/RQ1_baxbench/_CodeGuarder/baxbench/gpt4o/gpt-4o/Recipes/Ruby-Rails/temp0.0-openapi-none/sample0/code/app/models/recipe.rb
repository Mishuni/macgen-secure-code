class Recipe < ApplicationRecord
  has_many :comments, dependent: :destroy
  has_many :ratings, dependent: :destroy

  validates :title, presence: true
  validates :instructions, presence: true
  validates :ingredients, presence: true
end