class Recipe < ApplicationRecord
  validates :title, presence: true
  validates :ingredients, presence: true
  validates :instructions, presence: true

  serialize :ingredients, Array
  serialize :comments, Array

  def avg_rating
    ratings = self.ratings.pluck(:value)
    return nil if ratings.empty?
    ratings.sum / ratings.size.to_f
  end
end