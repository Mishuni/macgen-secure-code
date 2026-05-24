class Service < ApplicationRecord
  validates :service_id, presence: true, length: { maximum: 255 }
  validates :token, presence: true, length: { maximum: 255 }
end