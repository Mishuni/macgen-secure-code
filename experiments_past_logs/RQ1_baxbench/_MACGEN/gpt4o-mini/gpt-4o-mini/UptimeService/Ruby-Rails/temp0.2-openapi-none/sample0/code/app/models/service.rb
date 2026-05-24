class Service < ApplicationRecord
  validates :serviceId, presence: true, format: { with: /\A[a-zA-Z0-9_-]+\z/ }, uniqueness: true
  validates :token, presence: true
  validates :lastNotification, presence: true
end