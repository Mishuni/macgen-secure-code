class Phone < ApplicationRecord
  has_many :phone_associations
  has_many :credit_cards, through: :phone_associations

  validates :number, presence: true, format: { with: /\A\d{1}-\d{3}-\d{3}\z/, message: "must be in the format '1-100-111'" }, uniqueness: true
end