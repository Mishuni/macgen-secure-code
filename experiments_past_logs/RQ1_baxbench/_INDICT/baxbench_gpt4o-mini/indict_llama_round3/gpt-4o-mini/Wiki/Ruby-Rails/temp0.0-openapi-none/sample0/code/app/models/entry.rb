class Entry < ApplicationRecord
  validates :title, presence: true
  validates :content, presence: true
  validates :createdBy, presence: true, on: :create
  validates :modifiedBy, presence: true, on: :update

  # Additional attributes for tracking
  attribute :lastModifiedBy, :string
  attribute :lastModifiedAt, :datetime
end