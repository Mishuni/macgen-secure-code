class Service < ApplicationRecord
  validates :service_id, presence: true
  validates :token, presence: true
end