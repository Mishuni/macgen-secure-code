class CreditCard < ApplicationRecord
  has_many :phone_associations
  has_many :phones, through: :phone_associations

  validates :number, presence: true, format: { with: /\A\d{16}\z/, message: "must be a 16-digit number" }, uniqueness: true
end