class Comment < ApplicationRecord
  belongs_to :recipe

  validates :comment, presence: true, length: { maximum: 500 }
end