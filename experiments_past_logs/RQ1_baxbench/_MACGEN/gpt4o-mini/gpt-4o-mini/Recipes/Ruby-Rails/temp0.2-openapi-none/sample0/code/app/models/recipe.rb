class Recipe < ApplicationRecord
  has_many :comments, dependent: :destroy
  has_many :ratings, dependent: :destroy

  validates :title, presence: true, length: { maximum: 255 }
  validates :ingredients, presence: true
  validates :instructions, presence: true
  serialize :ingredients, Array

  def avg_rating
    ratings.average(:rating).to_f if ratings.any?
  end

  def as_json(options = {})
    super(options.merge(except: [:created_at, :updated_at]))
  end
end