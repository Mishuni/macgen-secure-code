class UserProfile < ApplicationRecord
  validates :username, presence: true, uniqueness: true
  validates :profile_page, presence: true
  validates :profile_photo, presence: true
  has_one_attached :profile_photo
end