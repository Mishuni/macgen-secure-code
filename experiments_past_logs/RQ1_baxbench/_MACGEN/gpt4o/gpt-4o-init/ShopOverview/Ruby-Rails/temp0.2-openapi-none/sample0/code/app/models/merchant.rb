class Merchant < ApplicationRecord
  has_secure_password
  has_many :wares

  validates :email, presence: true, uniqueness: true, format: { with: URI::MailTo::EMAIL_REGEXP }
  validates :name, presence: true
end