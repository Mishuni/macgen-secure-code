class PhoneAssociation < ApplicationRecord
  belongs_to :credit_card
  belongs_to :phone
end