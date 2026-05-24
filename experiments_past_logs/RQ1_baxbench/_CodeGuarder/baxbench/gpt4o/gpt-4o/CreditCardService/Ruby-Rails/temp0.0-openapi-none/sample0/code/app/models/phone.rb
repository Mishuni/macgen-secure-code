class Phone < ApplicationRecord
  has_many :phone_associations
  has_many :credit_cards, through: :phone_associations
end