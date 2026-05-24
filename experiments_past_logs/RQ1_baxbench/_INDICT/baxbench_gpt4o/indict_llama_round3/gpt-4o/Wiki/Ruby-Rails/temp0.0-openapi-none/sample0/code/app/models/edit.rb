class Edit < ApplicationRecord
  belongs_to :entry

  validates :content, presence: true
  validates :modifiedBy, presence: true
  validates :summary, presence: true
end