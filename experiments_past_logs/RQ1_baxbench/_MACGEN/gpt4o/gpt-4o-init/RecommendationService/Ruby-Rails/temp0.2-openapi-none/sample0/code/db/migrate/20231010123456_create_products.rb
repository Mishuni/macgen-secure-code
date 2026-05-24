class CreateProducts < ActiveRecord::Migration[8.0]
  def change
    create_table :products do |t|
      t.string :product_name, null: false
      t.text :tags, null: false

      t.timestamps
    end
  end
end