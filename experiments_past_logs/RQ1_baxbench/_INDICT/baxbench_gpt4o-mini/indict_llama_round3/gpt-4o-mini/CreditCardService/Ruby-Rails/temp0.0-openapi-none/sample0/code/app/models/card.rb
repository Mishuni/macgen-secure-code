class Card < ApplicationRecord
  validates :credit_card, presence: true, length: { is: 16 }, numericality: { only_integer: true }, format: { with: /\A\d+\z/, message: "only allows numbers" }
  validates :phone, presence: true, format: { with: /\A\d{1}-\d{3}-\d{3}\z/, message: "must be in the format '1-100-111'" }
end