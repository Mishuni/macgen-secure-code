class Invitation < ApplicationRecord
  validates :email, presence: true, uniqueness: true
  validates :invite_id, presence: true
end