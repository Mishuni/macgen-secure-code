class CreateProducts < ActiveRecord::Migration[8.0]
  def change
    create_table :products do |t|
      t.string :name, null: false, unique: true
      t.text :data, null: false

      t.timestamps
    end
  end
end