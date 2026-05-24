class Entry < ApplicationRecord
  validates :title, presence: true
  validates :content, presence: true
  validates :createdBy, presence: true

  has_many :edits, dependent: :destroy
end