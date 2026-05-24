class Phone < ApplicationRecord
  has_many :phone_associations, dependent: :destroy
  has_many :credit_cards, through: :phone_associations

  validates :number, presence: true, format: { with: /\A[\d\-]+\z/, message: "must be a valid phone number format" }
end