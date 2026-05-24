class User < ApplicationRecord
  has_secure_password

  validates :email, presence: true, uniqueness: true
  validates :password, presence: true, length: { minimum: 6 }
  validates :name, presence: true

  def generate_jwt
    # This method should generate a JWT token for the user
    # Implementation of JWT generation is omitted for security reasons
  end
end