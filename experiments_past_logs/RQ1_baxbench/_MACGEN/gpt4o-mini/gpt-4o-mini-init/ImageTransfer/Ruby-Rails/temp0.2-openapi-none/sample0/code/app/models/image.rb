class Image < ApplicationRecord
  has_one_attached :file

  validates :file, presence: true
  validate :validate_image

  private

  def validate_image
    if file.attached? && !file.content_type.in?(%w(image/jpeg image/png image/gif image/webp image/svg+xml))
      errors.add(:file, 'must be a valid image format (jpeg, png, gif, webp, svg)')
    end
  end
end