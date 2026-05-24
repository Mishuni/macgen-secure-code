class Invitation < ApplicationRecord
  validates :email, presence: true, uniqueness: true, format: { with: URI::MailTo::EMAIL_REGEXP }
  before_create :generate_invite_id

  private

  def generate_invite_id
    self.invite_id = SecureRandom.hex(10)
  end
end