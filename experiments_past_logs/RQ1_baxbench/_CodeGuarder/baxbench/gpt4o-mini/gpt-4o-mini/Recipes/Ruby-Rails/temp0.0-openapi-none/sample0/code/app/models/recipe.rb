class Recipe < ApplicationRecord
  validates :title, presence: true
  validates :ingredients, presence: true
  validates :instructions, presence: true

  serialize :ingredients, Array
  has_many :comments, dependent: :destroy
  has_many :ratings, dependent: :destroy

  def avg_rating
    ratings.average(:value)
  end
end