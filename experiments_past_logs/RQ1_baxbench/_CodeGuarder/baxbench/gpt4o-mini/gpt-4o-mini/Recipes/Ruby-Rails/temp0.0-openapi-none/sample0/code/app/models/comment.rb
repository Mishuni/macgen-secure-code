class Comment < ApplicationRecord
  belongs_to :recipe

  validates :comment, presence: true
end