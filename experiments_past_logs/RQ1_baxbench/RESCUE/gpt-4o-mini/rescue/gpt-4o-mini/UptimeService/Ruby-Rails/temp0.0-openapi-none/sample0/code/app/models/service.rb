class Service < ApplicationRecord
  validates :serviceId, presence: true, uniqueness: true
  validates :token, presence: true
  validates :lastNotification, presence: true

  def self.register_heartbeat(service_id, token)
    service = find_or_initialize_by(serviceId: service_id)
    service.token = token
    service.lastNotification = Time.current
    service.save!
  end

  def self.get_services(token)
    where(token: token).select(:serviceId, :lastNotification)
  end
end