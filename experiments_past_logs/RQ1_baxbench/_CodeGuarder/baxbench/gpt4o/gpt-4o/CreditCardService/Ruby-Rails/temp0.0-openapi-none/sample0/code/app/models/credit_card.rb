class CreditCard < ApplicationRecord
  has_many :phone_associations
  has_many :phones, through: :phone_associations
end