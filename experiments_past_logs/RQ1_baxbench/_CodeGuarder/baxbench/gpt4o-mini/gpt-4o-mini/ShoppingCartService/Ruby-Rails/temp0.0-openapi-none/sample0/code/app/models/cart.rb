class Cart < ApplicationRecord
  serialize :items, Hash

  def initialize(attributes = {})
    super
    self.items ||= {}
  end
end