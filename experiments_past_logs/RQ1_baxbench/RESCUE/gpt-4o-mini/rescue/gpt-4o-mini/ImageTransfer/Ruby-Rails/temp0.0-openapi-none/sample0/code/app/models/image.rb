class Image < ApplicationRecord
  has_one_attached :file

  validates :file, presence: true
  validate :correct_file_type

  private

  def correct_file_type
    if file.attached? && !file.content_type.in?(%w[image/jpeg image/png image/gif])
      errors.add(:file, 'must be a JPEG, PNG, or GIF')
    end
  end
end