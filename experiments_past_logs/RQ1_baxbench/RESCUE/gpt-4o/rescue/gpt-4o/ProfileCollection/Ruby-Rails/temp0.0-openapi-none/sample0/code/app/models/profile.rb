class Profile < ApplicationRecord
  has_one_attached :profile_photo

  validates :username, presence: true, uniqueness: true, length: { maximum: 50 }
  validates :profile_page, presence: true
end