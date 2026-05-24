class User < ApplicationRecord
  has_secure_password

  validates :user_name, presence: true, uniqueness: true, format: { with: /\A[a-zA-Z0-9_]+\z/, message: "only allows letters, numbers, and underscores" }
  validates :password, presence: true, length: { minimum: 6 }
end