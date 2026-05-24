class Profile < ApplicationRecord
  has_one_attached :profile_photo
  validates :username, presence: true, uniqueness: true
  validates :profile_page, presence: true
  validate :profile_photo_format

  private

  def profile_photo_format
    return unless profile_photo.attached?
    if profile_photo.blob.content_type != 'image/png'
      profile_photo.purge
      errors.add(:profile_photo, 'must be a PNG file')
    end
  end
end