class Service < ApplicationRecord
  validates :service_id, presence: true, uniqueness: true
  validates :token, presence: true
end