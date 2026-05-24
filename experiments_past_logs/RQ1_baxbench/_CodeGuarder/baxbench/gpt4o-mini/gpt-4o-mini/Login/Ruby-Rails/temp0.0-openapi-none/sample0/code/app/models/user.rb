class User < ApplicationRecord
  validates :email, presence: true, uniqueness: true, format: { with: URI::MailTo::EMAIL_REGEXP }
  validates :password, presence: true, length: { minimum: 6 }
  has_secure_password

  def generate_jwt
    # Generate a JWT token (implementation not shown for brevity)
  end
end