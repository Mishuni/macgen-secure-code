class CreditCardAssociation < ApplicationRecord
  validates :credit_card, presence: true, format: { with: /\A\d{16}\z/, message: "must be 16 digits" }
  validates :phone, presence: true, format: { with: /\A\d{1}-\d{3}-\d{3}\z/, message: "must be in the format '1-100-111'" }

  before_save :encrypt_credit_card

  def encrypt_credit_card
    self.credit_card = encrypt(self.credit_card)
  end

  private

  def encrypt(data)
    # Simple encryption logic (for demonstration purposes)
    # In a real application, use a strong encryption algorithm like AES
    cipher = OpenSSL::Cipher::AES.new(256, :CBC)
    cipher.encrypt
    cipher.key = ENV['APP_SECRET'][0..31] # Ensure the key is 32 bytes for AES-256
    iv = cipher.random_iv
    cipher.iv = iv
    encrypted = cipher.update(data) + cipher.final
    "#{Base64.encode64(iv)}--#{Base64.encode64(encrypted)}"
  end
end