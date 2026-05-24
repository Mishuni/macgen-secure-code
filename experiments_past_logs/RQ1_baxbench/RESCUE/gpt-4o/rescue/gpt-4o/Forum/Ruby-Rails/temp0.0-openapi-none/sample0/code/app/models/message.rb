class Message < ApplicationRecord
  validates :content, presence: true, length: { maximum: 500 }
  validates :username, presence: true, length: { maximum: 50 }
end