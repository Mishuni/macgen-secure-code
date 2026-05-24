class Secret < ApplicationRecord
  belongs_to :user

  validates :secret, presence: true
end