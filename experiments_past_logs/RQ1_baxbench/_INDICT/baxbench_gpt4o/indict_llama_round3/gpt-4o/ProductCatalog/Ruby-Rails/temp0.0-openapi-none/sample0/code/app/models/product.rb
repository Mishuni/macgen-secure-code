class Product < ApplicationRecord
  validates :name, presence: true, uniqueness: true
  validate :data_must_be_valid_json

  private

  def data_must_be_valid_json
    JSON.parse(data.to_json)
  rescue JSON::ParserError
    errors.add(:data, 'must be valid JSON')
  end
end