class Product < ApplicationRecord
  serialize :tags, Array
end