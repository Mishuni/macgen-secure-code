class Profile < ApplicationRecord
  has_one_attached :photo

  validates :username, presence: true, uniqueness: true
  validates :profile_page, presence: true
end