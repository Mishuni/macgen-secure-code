class UserProfile < ApplicationRecord
  has_one_attached :profile_photo

  validates :username, presence: true, uniqueness: true
  validates :profile_page, presence: true
  validates :profile_photo, content_type: ['image/png'] # Validate file type
end