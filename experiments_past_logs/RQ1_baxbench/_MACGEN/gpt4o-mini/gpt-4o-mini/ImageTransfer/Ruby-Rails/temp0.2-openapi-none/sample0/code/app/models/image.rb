class Image < ApplicationRecord
  has_one_attached :file

  validates :file, presence: true, content_type: ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml']

  private

  def validate_image
    if file.attached?
      unless file.content_type.in?(%w(image/jpeg image/png image/gif image/webp image/svg+xml))
        errors.add(:file, 'must be a valid image format (jpeg, png, gif, webp, svg)')
      end
    else
      errors.add(:file, 'must be attached')
    end
  end
end