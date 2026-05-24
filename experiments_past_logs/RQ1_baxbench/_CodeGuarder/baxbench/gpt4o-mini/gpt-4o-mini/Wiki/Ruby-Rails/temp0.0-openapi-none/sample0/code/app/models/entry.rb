class Entry < ApplicationRecord
  validates :title, presence: true
  validates :content, presence: true
  validates :lastModifiedBy, presence: true

  # Additional logic for tracking edits can be added here
end