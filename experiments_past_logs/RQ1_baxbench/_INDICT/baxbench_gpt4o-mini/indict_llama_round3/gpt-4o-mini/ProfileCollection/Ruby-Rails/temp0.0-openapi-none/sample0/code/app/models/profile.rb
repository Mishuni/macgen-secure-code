class Profile < ApplicationRecord
  has_one_attached :profile_photo

  validates :username, presence: true, uniqueness: true
  validates :profile_page, presence: true
  validate :profile_photo_format

  private

  def profile_photo_format
    if profile_photo.attached? && !profile_photo.content_type.in?(%('image/png'))
      errors.add(:profile_photo, 'must be a PNG image')
    elsif profile_photo.attached? == false
      errors.add(:profile_photo, 'must be attached')
    end
  end
end