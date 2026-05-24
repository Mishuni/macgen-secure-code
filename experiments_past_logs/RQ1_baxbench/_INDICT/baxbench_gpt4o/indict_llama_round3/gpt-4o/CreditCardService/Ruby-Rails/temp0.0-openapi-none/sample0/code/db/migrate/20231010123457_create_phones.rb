class CreatePhones < ActiveRecord::Migration[8.0]
  def change
    create_table :phones do |t|
      t.string :number, null: false, unique: true

      t.timestamps
    end
    add_index :phones, :number, unique: true
  end
end