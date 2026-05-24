class Click < ApplicationRecord
  validates :id, presence: true, uniqueness: true
  validates :timestamp, presence: true
end