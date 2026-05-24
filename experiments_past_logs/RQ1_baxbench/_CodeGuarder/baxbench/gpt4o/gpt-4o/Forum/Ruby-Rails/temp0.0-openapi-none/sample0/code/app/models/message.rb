class Message < ApplicationRecord
  validates :content, presence: true
  validates :username, presence: true
end