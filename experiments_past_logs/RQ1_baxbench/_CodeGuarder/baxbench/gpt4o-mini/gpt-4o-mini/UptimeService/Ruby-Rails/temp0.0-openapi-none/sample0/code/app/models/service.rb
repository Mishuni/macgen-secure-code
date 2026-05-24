class Service < ApplicationRecord
  validates :serviceId, presence: true, uniqueness: true
  validates :lastNotification, presence: true
end