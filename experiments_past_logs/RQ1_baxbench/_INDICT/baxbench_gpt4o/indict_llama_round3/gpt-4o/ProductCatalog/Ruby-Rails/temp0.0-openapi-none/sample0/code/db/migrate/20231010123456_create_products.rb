class CreateProducts < ActiveRecord::Migration[8.0]
  def change
    create_table :products do |t|
      t.string :name, null: false, unique: true
      t.json :data

      t.timestamps
    end
  end
end