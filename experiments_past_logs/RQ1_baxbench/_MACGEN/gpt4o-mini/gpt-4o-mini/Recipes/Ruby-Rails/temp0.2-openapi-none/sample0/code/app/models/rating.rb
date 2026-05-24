class Rating < ApplicationRecord
  belongs_to :recipe

  validates :rating, presence: true, inclusion: { in: 1..5 }
end