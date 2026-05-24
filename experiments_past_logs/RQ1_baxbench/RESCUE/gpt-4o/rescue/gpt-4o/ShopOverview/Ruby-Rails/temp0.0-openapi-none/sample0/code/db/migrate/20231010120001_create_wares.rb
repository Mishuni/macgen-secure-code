class CreateWares < ActiveRecord::Migration[7.0]
  def change
    create_table :wares do |t|
      t.string :name, null: false
      t.text :description, null: false
      t.decimal :price, null: false, precision: 10, scale: 2
      t.references :merchant, null: false, foreign_key: true

      t.timestamps
    end
  end
end