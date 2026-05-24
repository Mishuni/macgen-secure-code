class CreditCardPhoneAssociation < ApplicationRecord
  validates :credit_card, presence: true
  validates :phone, presence: true
end