class Entry < ApplicationRecord
  validates :title, presence: true
  validates :content, presence: true
  validates :createdBy, presence: true

  def edits
    [] # Placeholder for edit history
  end
end