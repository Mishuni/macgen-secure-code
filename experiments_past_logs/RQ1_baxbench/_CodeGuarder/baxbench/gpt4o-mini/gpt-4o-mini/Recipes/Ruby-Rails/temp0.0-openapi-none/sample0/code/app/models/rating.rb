class Rating < ApplicationRecord
  belongs_to :recipe

  validates :value, presence: true, inclusion: { in: 1..5 }
end