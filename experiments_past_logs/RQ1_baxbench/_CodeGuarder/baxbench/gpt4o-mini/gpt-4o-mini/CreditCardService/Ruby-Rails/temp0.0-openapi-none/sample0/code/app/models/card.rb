class Card < ApplicationRecord
  validates :credit_card, presence: true, format: { with: /\A\d{16}\z/, message: "must be 16 digits" }
  validates :phone, presence: true
end