class Service < ApplicationRecord
  has_secure_password :token, validations: false

  validates :service_id, presence: true
  validates :token_digest, presence: true

  def self.digest(token)
    BCrypt::Password.create(token)
  end

  def authenticate_token(token)
    BCrypt::Password.new(token_digest).is_password?(token)
  end
end