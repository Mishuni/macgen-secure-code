class Entry < ApplicationRecord
  validates :title, presence: true
  validates :content, presence: true
  validates :createdBy, presence: true

  def edits
    # This method should return the history of edits for the entry
    # Implement logic to track and return edit history
  end
end