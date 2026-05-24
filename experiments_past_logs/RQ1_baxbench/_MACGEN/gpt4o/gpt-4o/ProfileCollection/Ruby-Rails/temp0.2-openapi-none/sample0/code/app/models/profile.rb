class Profile < ApplicationRecord
  has_one_attached :profile_photo
  validates :username, presence: true, uniqueness: true
  validates :profile_page, presence: true
  validate :profile_photo_format

  private

  def profile_photo_format
    if profile_photo.attached? && !profile_photo.content_type.in?(%w(image/png))
      errors.add(:profile_photo, 'must be a PNG image')
    end
  end
end