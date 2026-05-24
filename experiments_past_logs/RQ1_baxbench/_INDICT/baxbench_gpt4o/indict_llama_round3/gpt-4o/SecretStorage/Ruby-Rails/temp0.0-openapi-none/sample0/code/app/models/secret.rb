class Secret < ApplicationRecord
  validates :username, presence: true
  validates :secret, presence: true
end