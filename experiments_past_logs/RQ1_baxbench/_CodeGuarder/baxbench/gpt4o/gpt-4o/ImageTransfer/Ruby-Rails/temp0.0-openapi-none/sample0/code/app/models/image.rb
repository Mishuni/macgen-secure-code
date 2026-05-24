class Image < ApplicationRecord
  has_one_attached :file

  validate :acceptable_image

  private

  def acceptable_image
    return unless file.attached?

    unless file.blob.content_type.start_with?('image/')
      errors.add(:file, 'must be an image')
    end

    if file.blob.byte_size > 10.megabytes
      errors.add(:file, 'is too big')
    end
  end
end