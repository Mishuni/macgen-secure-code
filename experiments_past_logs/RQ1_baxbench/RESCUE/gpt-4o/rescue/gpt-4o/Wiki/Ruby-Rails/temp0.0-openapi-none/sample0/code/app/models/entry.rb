class Entry < ApplicationRecord
  validates :title, presence: true, length: { maximum: 255 }
  validates :content, presence: true
  validates :created_by, presence: true, length: { maximum: 255 }
end