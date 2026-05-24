class Secret < ApplicationRecord
  belongs_to :user

  validates :username, presence: true
  validates :secret, presence: true
end