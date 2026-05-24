class Rating < ApplicationRecord
  belongs_to :recipe

  validates :value, inclusion: { in: 1..5 }
end