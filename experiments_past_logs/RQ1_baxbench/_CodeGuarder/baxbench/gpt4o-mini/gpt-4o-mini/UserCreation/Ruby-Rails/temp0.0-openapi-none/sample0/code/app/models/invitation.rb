class Invitation < ApplicationRecord
  validates :email, presence: true, format: { with: URI::MailTo::EMAIL_REGEXP }, uniqueness: true
  before_create :generate_invite_id

  private

  def generate_invite_id
    self.invite_id = SecureRandom.uuid
  end
end